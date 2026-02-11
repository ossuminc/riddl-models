import com.ossuminc.sbt.OssumIncPlugin
import sbt.Keys._

import scala.sys.process._

Global / onChangedBuildSource := ReloadOnSourceChanges

enablePlugins(OssumIncPlugin)

lazy val riddlLibVersion = "1.3.1"
lazy val riddlcVersion = "1.7.0"

// Custom task keys
lazy val downloadRiddlc = taskKey[File](
  "Download and cache the riddlc binary from GitHub releases"
)
lazy val riddlcValidateAll = taskKey[Unit](
  "Validate all RIDDL models using riddlc"
)

lazy val riddlModels = Root("riddl-models", startYr = 2026, spdx = "Apache-2.0")
  .configure(With.typical)  // Sets up Scala 3.3.x and resolvers
  .configure(With.noPublishing, With.Git, With.DynVer, With.noMiMa)
  .settings(
    description := "Library of RIDDL models and reusable patterns",
    libraryDependencies ++= Seq(
      "com.ossuminc" %% "riddl-lib" % riddlLibVersion % Test,
      "org.scalatest" %% "scalatest" % "3.2.19" % Test
    ),
    // Make the base directory available as a system property for the test
    Test / javaOptions +=
      s"-Driddl.models.basedir=${baseDirectory.value.getAbsolutePath}",
    Test / fork := true,

    // --- riddlc download and validation ---

    downloadRiddlc := {
      val log = streams.value.log
      val cacheDir = baseDirectory.value / ".riddlc" / riddlcVersion
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
          "riddlc.zip" // JVM universal package (requires Java)
        }
      }

      val binary = cacheDir / "bin" / "riddlc"

      if (!binary.exists()) {
        log.info(s"Downloading riddlc $riddlcVersion ($assetName)...")
        IO.createDirectory(cacheDir)
        val zipFile = cacheDir / assetName
        val url =
          s"https://github.com/ossuminc/riddl/releases/download/$riddlcVersion/$assetName"
        Process(Seq("curl", "-fSL", "-o", zipFile.getAbsolutePath, url)).!!
        IO.unzip(zipFile, cacheDir)
        binary.setExecutable(true)
        IO.delete(zipFile)
        log.info(
          s"riddlc $riddlcVersion installed to ${binary.getAbsolutePath}"
        )
      }

      binary
    },

    riddlcValidateAll := {
      val log = streams.value.log
      val binary = downloadRiddlc.value
      val base = baseDirectory.value

      // Find all .conf files, excluding non-model directories
      val confFiles = ((base ** "*.conf")
        --- (base / "patterns" ** "*.conf")
        --- (base / "target" ** "*.conf")
        --- (base / "project" ** "*.conf")
        --- (base / ".riddlc" ** "*.conf")).get.sorted

      log.info(
        s"Validating ${confFiles.size} RIDDL models with riddlc $riddlcVersion..."
      )

      var failures = List.empty[(String, String)]
      confFiles.foreach { conf =>
        val relPath = base.toPath.relativize(conf.toPath).toString
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
    },

    // Wire validation into compile
    Compile / compile := {
      riddlcValidateAll.value
      (Compile / compile).value
    }
  )

// Command aliases
addCommandAlias("validate", "riddlcValidateAll")
addCommandAlias("v", "riddlcValidateAll")
