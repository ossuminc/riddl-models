import com.ossuminc.sbt.OssumIncPlugin
import com.ossuminc.riddl.sbt.plugin.RiddlSbtPlugin
import sbt.Keys._

Global / onChangedBuildSource := ReloadOnSourceChanges

enablePlugins(OssumIncPlugin)
enablePlugins(RiddlSbtPlugin)

lazy val riddlModels = Root("riddl-models", startYr = 2026, spdx = "Apache-2.0")
  .configure(With.typical)  // Sets up Scala 3.3.x and resolvers
  .configure(With.noPublishing, With.Git, With.DynVer, With.noMiMa)
  .settings(
    description := "Library of RIDDL models and reusable patterns",
    libraryDependencies ++= Seq(
      "com.ossuminc" %% "riddl-lib" % "1.13.2" % Test,
      "org.scalatest" %% "scalatest" % "3.2.19" % Test
    ),
    // Make the base directory available as a system property for the test
    Test / javaOptions +=
      s"-Driddl.models.basedir=${baseDirectory.value.getAbsolutePath}",
    Test / fork := true,

    // --- sbt-riddl configuration ---
    riddlcVersion := "1.13.1",
    riddlcSourceDir := baseDirectory.value,
    riddlcConfExclusions := Seq("patterns"),
    riddlcValidateOnCompile := true,
    riddlcOptions := Seq("--show-times", "--no-ansi-messages")
  )

// Command aliases (plugin provides validate, bastify, prettify)
addCommandAlias("v", "riddlcValidate")
addCommandAlias("b", "riddlcBastify")
addCommandAlias("r", "riddlcPrettify")
