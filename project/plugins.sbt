// Ossum Inc SBT plugin for standardized build configuration
addSbtPlugin("com.ossuminc" % "sbt-ossuminc" % "1.3.5")

// RIDDL compiler sbt plugin (validate, bastify, prettify, etc.)
addSbtPlugin("com.ossuminc" % "sbt-riddl" % "1.13.1")

// Credentials for GitHub Packages
credentials ++= {
  val home = System.getProperty("user.home")
  val credsFile = file(s"$home/.sbt/1.0/github.sbt")
  if (credsFile.exists()) {
    // The credentials file will be loaded by sbt automatically
    Seq.empty
  } else {
    sys.env.get("GITHUB_TOKEN").map { token =>
      Credentials(
        "GitHub Package Registry",
        "maven.pkg.github.com",
        sys.env.getOrElse("GITHUB_ACTOR", "token"),
        token
      )
    }.toSeq
  }
}

resolvers ++= Seq(
  "GitHub Packages - ossuminc" at "https://maven.pkg.github.com/ossuminc/sbt-ossuminc",
  "GitHub Packages - riddl" at "https://maven.pkg.github.com/ossuminc/riddl"
)