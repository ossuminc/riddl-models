import com.ossuminc.sbt.OssumIncPlugin
import sbt.Keys._

Global / onChangedBuildSource := ReloadOnSourceChanges

enablePlugins(OssumIncPlugin)

lazy val riddlVersion = "1.10.2"

// Custom task keys
lazy val downloadRiddlc = taskKey[File](
  "Download and cache the riddlc binary from GitHub releases"
)
lazy val riddlcValidateAll = taskKey[Unit](
  "Validate all RIDDL models using riddlc"
)
lazy val riddlcBastifyAll = taskKey[Unit](
  "Generate .bast files for all RIDDL models using riddlc bastify"
)

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
    Test / javaOptions +=
      s"-Driddl.models.basedir=${baseDirectory.value.getAbsolutePath}",
    Test / fork := true,

    // --- riddlc tasks ---

    downloadRiddlc := {
      RiddlcTasks.downloadRiddlc(
        baseDirectory.value,
        riddlVersion,
        streams.value.log
      )
    },

    riddlcValidateAll := {
      RiddlcTasks.validateAll(
        downloadRiddlc.value,
        baseDirectory.value,
        riddlVersion,
        streams.value.log
      )
    },

    riddlcBastifyAll := {
      RiddlcTasks.bastifyAll(
        downloadRiddlc.value,
        baseDirectory.value,
        riddlVersion,
        streams.value.log
      )
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
addCommandAlias("bastify", "riddlcBastifyAll")
addCommandAlias("b", "riddlcBastifyAll")
