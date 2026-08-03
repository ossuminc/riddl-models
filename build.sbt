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
    riddlcVersion := "2.0.0-rc.9-42-37b0db94",

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
    // `test` is an InputTask in sbt 2, so hook executeTests, which `sbt test`
    // runs anyway. Def.uncached because Tests.Output has no JsonFormat and so
    // cannot be a cached result.
    Test / executeTests := Def.uncached(
      (Test / executeTests).dependsOn(verifyTemplates)
    ).value
  )

// Command aliases (plugin provides validate, bastify, prettify)
addCommandAlias("v", "riddlcValidate")
addCommandAlias("b", "riddlcBastify")
addCommandAlias("r", "riddlcPrettify")
addCommandAlias("vt", "verifyTemplates")
