import com.ossuminc.sbt.OssumIncPlugin
import com.ossuminc.riddl.sbt.plugin.RiddlSbtPlugin
import sbt.Keys._
import scala.sys.process.{Process, ProcessLogger}

Global / onChangedBuildSource := ReloadOnSourceChanges

enablePlugins(OssumIncPlugin)
enablePlugins(RiddlSbtPlugin)

// `riddlcConfExclusions` below excludes patterns/ from riddlcValidate, so
// nothing in the build looked at it -- and the pattern templates rotted through
// the whole RIDDL 2.0 migration without anyone noticing. This task is what
// covers that hole. It is wired into riddlcValidate and Test/test below, so the
// exclusion can no longer hide anything.
// The riddlc binary and the riddl libraries the test suite uses come from the
// same build, so one value pins both. While riddl's release/2 is being
// perfected the binary is staged at ../bin/riddlc and the libraries arrive by
// `sbt publishLocal` from that checkout, so this moves in step with riddl
// rather than tracking published releases.
lazy val riddlVersion = "2.0.0-rc.12-4-092ec2be"

lazy val verifyTemplates = taskKey[Unit](
  "Check patterns/: validate the examples, and parse the templates after " +
    "substituting their {Placeholder} names"
)

lazy val riddlModels = Root("riddl-models", startYr = 2026, spdx = "Apache-2.0")
  .configure(With.typical)  // Sets up Scala 3.3.x and resolvers
  .configure(With.noPublishing, With.Git, With.DynVer, With.noMiMa,
    riddlc(sourceDir = ".", validateOnCompile = false))
  .settings(
    // Make the base directory available as a system property for the test
    Test / javaOptions +=
      s"-Driddl.models.basedir=${baseDirectory.value.getAbsolutePath}",
    Test / fork := true,

    // --- sbt-riddl configuration ---
    // riddlcVersion is pinned even though it matches the plugin: the plugin
    // shells out to a riddlc binary, so plugin version and language version are
    // independent, and pinning states which parser the corpus is validated
    // against rather than inheriting the plugin's default.
    // Must match the Scala version riddl publishes with: its TASTy is not
    // readable by an older compiler, and the test suite links those libraries
    // directly. If `Test/compile` starts failing with "TASTy file ... could not
    // be read", this is what drifted.
    scalaVersion := "3.9.0-RC4",

    riddlcVersion := riddlVersion,

    // The test suite validates the corpus through the library API, which is a
    // different path from the CLI that riddlcValidate drives. These resolve
    // from the local ivy repository while release/2 is in flight.
    libraryDependencies ++= Seq(
      "com.ossuminc" %% "riddl-language" % riddlVersion % Test,
      "com.ossuminc" %% "riddl-passes" % riddlVersion % Test,
      "com.ossuminc" %% "riddl-utils" % riddlVersion % Test
    ),

    // That version is STAGED, not published, so it cannot be downloaded. Use a
    // staged ../bin/riddlc when one is there, and fall back to the download
    // otherwise -- which is what will happen once the version ships, and what
    // happens for anyone who does not keep a riddl checkout beside this one.
    // Without this, `sbt v` fails on `riddlcBinary` with a bare "Nonzero exit
    // value: 56" from the download.
    riddlcPath := {
      val staged = baseDirectory.value.getParentFile / "bin" / "riddlc"
      if (staged.exists() && staged.canExecute) Some(staged) else None
    },
    riddlcSourceDir := baseDirectory.value,
    riddlcConfExclusions := Seq("patterns"),
    riddlcOptions := Seq("--show-times", "--no-ansi-messages"),

    // Runs scripts/verify-templates.py against the same riddlc the rest of the
    // build uses, so a staged binary named by `riddlcPath` is honoured here too
    // rather than the script falling back to its own default.
    //
    // Def.uncached because the task takes no inputs sbt can hash: without it,
    // sbt 2 records the first Unit result and never runs the script again.
    verifyTemplates := Def.uncached {
      val log = streams.value.log
      val base = baseDirectory.value
      val riddlc = riddlcBinary.value
      val script = base / "scripts" / "verify-templates.py"
      if (!script.exists()) {
        sys.error(s"verify-templates.py not found at $script")
      }
      log.info("Checking patterns/ (examples validate, templates parse)")
      val forward = ProcessLogger(l => log.info(l), l => log.error(l))
      val code = Process(
        Seq("python3", script.getAbsolutePath),
        base,
        "RIDDLC" -> riddlc.getAbsolutePath
      ) ! forward
      if (code != 0) {
        sys.error(
          "patterns/ check failed. Templates are excluded from riddlcValidate, " +
            "so this task is the only thing that checks them -- see the output above."
        )
      }
    },

    // patterns/ is excluded from riddlcValidate, so bolt the check onto it:
    // `sbt v` now means the whole repository, not just the 187 gated models.
    riddlcValidate := riddlcValidate.dependsOn(verifyTemplates).value,
    // `test` is an InputTask in sbt 2, so this is `.evaluated` rather than
    // `.value`. Note sbt 2 routes `test` to testQuick, which skips unchanged
    // tests -- and this suite reads .riddl files at RUN time, so sbt cannot see
    // a model change as an input. `sbt test` is therefore a weak gate for model
    // edits; `sbt checkAll` below forces the full suite.
    Test / test := ((Test / test) dependsOn verifyTemplates).evaluated
  )

// Command aliases (plugin provides validate, bastify, prettify)
addCommandAlias("v", "riddlcValidate")
addCommandAlias("b", "riddlcBastify")
addCommandAlias("r", "riddlcPrettify")
addCommandAlias("vt", "verifyTemplates")

// The whole-repository gate: patterns, the corpus through the CLI, and the
// corpus again through the library API. executeTests rather than test, because
// the latter skips tests sbt believes are unchanged.
addCommandAlias("checkAll", "; riddlcValidate; Test/executeTests")
