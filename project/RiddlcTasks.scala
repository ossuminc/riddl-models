import sbt._
import scala.sys.process._
import scala.util.matching.Regex

object RiddlcTasks {

  /** Download and cache the riddlc binary from GitHub releases. */
  def downloadRiddlc(
    baseDir: File,
    version: String,
    log: Logger
  ): File = {
    val cacheDir = baseDir / ".riddlc" / version
    val osName = sys.props.getOrElse("os.name", "").toLowerCase
    val osArch = sys.props.getOrElse("os.arch", "").toLowerCase

    val assetName = {
      if (osName.contains("mac") &&
          (osArch.contains("aarch64") || osArch.contains("arm64"))) {
        "riddlc-macos-arm64.zip"
      } else if (osName.contains("linux") &&
                 (osArch.contains("amd64") || osArch.contains("x86_64"))) {
        "riddlc-linux-x86_64.zip"
      } else {
        "riddlc.zip"
      }
    }

    val binary = cacheDir / "bin" / "riddlc"

    if (!binary.exists()) {
      log.info(s"Downloading riddlc $version ($assetName)...")
      IO.createDirectory(cacheDir)
      val zipFile = cacheDir / assetName
      val url =
        s"https://github.com/ossuminc/riddl/releases/download/$version/$assetName"
      Process(Seq("curl", "-fSL", "-o", zipFile.getAbsolutePath, url)).!!
      IO.unzip(zipFile, cacheDir)
      binary.setExecutable(true)
      IO.delete(zipFile)
      log.info(s"riddlc $version installed to ${binary.getAbsolutePath}")
    }

    binary
  }

  /** Find all model .conf files, excluding non-model directories. */
  def findConfFiles(baseDir: File): Seq[File] = {
    ((baseDir ** "*.conf")
      --- (baseDir / "patterns" ** "*.conf")
      --- (baseDir / "target" ** "*.conf")
      --- (baseDir / "project" ** "*.conf")
      --- (baseDir / ".riddlc" ** "*.conf")).get.sorted
  }

  /** Validate all RIDDL models using riddlc. */
  def validateAll(
    binary: File,
    baseDir: File,
    version: String,
    log: Logger
  ): Unit = {
    val confFiles = findConfFiles(baseDir)

    log.info(
      s"Validating ${confFiles.size} RIDDL models with riddlc $version..."
    )

    var failures = List.empty[(String, String)]
    confFiles.foreach { conf =>
      val relPath = baseDir.toPath.relativize(conf.toPath).toString
      val errOutput = new StringBuilder
      val outOutput = new StringBuilder
      val logger = ProcessLogger(
        out => outOutput.append(out).append("\n"),
        err => errOutput.append(err).append("\n")
      )
      val exitCode = Process(
        Seq(binary.getAbsolutePath, "from", conf.getAbsolutePath, "validate"),
        conf.getParentFile
      ).!(logger)

      if (exitCode != 0) {
        val detail = if (errOutput.nonEmpty) errOutput.toString.trim
                     else outOutput.toString.trim
        failures = (relPath, detail) :: failures
        log.error(s"  FAILED: $relPath")
      } else {
        log.info(s"  OK: $relPath")
      }
    }

    if (failures.nonEmpty) {
      log.error("")
      log.error(s"${failures.size} model(s) failed validation:")
      failures.reverse.foreach { case (path, detail) =>
        log.error(s"--- $path ---")
        if (detail.nonEmpty) { log.error(detail) }
      }
      sys.error(
        s"${failures.size} of ${confFiles.size} models failed riddlc validation"
      )
    } else {
      log.info(s"All ${confFiles.size} models validated successfully.")
    }
  }

  private val InputFilePattern: Regex =
    """input-file\s*=\s*"([^"]+)"""".r

  /** Extract input-file value from a .conf file. */
  def extractInputFile(conf: File): Option[String] = {
    val content = IO.read(conf)
    InputFilePattern.findFirstMatchIn(content).map(_.group(1))
  }

  /** Generate .bast files for all RIDDL models using riddlc bastify. */
  def bastifyAll(
    binary: File,
    baseDir: File,
    version: String,
    log: Logger
  ): Unit = {
    val confFiles = findConfFiles(baseDir)

    log.info(
      s"Generating .bast files for ${confFiles.size} RIDDL models " +
      s"with riddlc $version..."
    )

    var failures = List.empty[(String, String)]
    var successes = 0
    confFiles.foreach { conf =>
      val relPath = baseDir.toPath.relativize(conf.toPath).toString
      extractInputFile(conf) match {
        case None =>
          val msg = "Could not extract input-file from conf"
          failures = (relPath, msg) :: failures
          log.error(s"  FAILED: $relPath - $msg")

        case Some(inputFile) =>
          val modelDir = conf.getParentFile
          val riddlFile = modelDir / inputFile
          val errOutput = new StringBuilder
          val outOutput = new StringBuilder
          val logger = ProcessLogger(
            out => outOutput.append(out).append("\n"),
            err => errOutput.append(err).append("\n")
          )
          val exitCode = Process(
            Seq(
              binary.getAbsolutePath,
              "bastify",
              riddlFile.getAbsolutePath
            ),
            modelDir
          ).!(logger)

          if (exitCode != 0) {
            val detail = if (errOutput.nonEmpty) errOutput.toString.trim
                         else outOutput.toString.trim
            failures = (relPath, detail) :: failures
            log.error(s"  FAILED: $relPath")
          } else {
            successes += 1
            log.info(s"  OK: $relPath")
          }
      }
    }

    if (failures.nonEmpty) {
      log.error("")
      log.error(s"${failures.size} model(s) failed bastify:")
      failures.reverse.foreach { case (path, detail) =>
        log.error(s"--- $path ---")
        if (detail.nonEmpty) { log.error(detail) }
      }
      log.info(s"$successes succeeded, ${failures.size} failed.")
      sys.error(
        s"${failures.size} of ${confFiles.size} models failed riddlc bastify"
      )
    } else {
      log.info(
        s"All ${confFiles.size} models bastified successfully " +
        s"($successes .bast files generated)."
      )
    }
  }
}
