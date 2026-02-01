import com.ossuminc.sbt.OssumIncPlugin
import sbt.Keys.*

Global / onChangedBuildSource := ReloadOnSourceChanges

enablePlugins(OssumIncPlugin)

lazy val riddlVersion = "1.1.1"

lazy val riddlModels = Root("riddl-models", startYr = 2026, spdx = "Apache-2.0")
  .configure(With.typical)  // Sets up Scala 3.3.x and resolvers
  .configure(With.noPublishing, With.Git, With.DynVer, With.noMiMa)
  .settings(
    description := "Library of RIDDL models and reusable patterns",
    libraryDependencies ++= Seq(
      "com.ossuminc" %% "riddl-lib" % riddlVersion % Test,
      "org.scalatest" %% "scalatest" % "3.2.19" % Test
    ),
    // Make the base directory available as a system property for the test
    Test / javaOptions += s"-Driddl.models.basedir=${baseDirectory.value.getAbsolutePath}",
    Test / fork := true
  )

// Command aliases
addCommandAlias("validate", "test")
addCommandAlias("v", "test")