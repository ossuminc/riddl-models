import com.ossuminc.sbt.OssumIncPlugin
import com.ossuminc.riddl.sbt.plugin.RiddlSbtPlugin
import sbt.Keys._

Global / onChangedBuildSource := ReloadOnSourceChanges

enablePlugins(OssumIncPlugin)
enablePlugins(RiddlSbtPlugin)

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
    riddlcVersion := "2.0.0-rc.9-29-989b7f46",
    riddlcSourceDir := baseDirectory.value,
    riddlcConfExclusions := Seq("patterns"),
    riddlcOptions := Seq("--show-times", "--no-ansi-messages")
  )

// Command aliases (plugin provides validate, bastify, prettify)
addCommandAlias("v", "riddlcValidate")
addCommandAlias("b", "riddlcBastify")
addCommandAlias("r", "riddlcPrettify")
