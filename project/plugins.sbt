// GitHub Packages resolvers for sbt-ossuminc and sbt-riddl
resolvers += "GitHub Packages - ossuminc" at
  "https://maven.pkg.github.com/ossuminc/sbt-ossuminc"
resolvers += "GitHub Packages - riddl" at
  "https://maven.pkg.github.com/ossuminc/riddl"

// Credentials MUST live in the meta-build (here), not only in the global
// ~/.sbt/2/github.sbt: under sbt 2 the global credentials file is not applied
// to meta-build (plugin) resolution, so plugin fetches from GitHub Packages get
// a 401 despite a valid GITHUB_TOKEN.
credentials += Credentials(
  "GitHub Package Registry",
  "maven.pkg.github.com",
  "x-access-token",
  sys.env.getOrElse("GITHUB_TOKEN", "")
)

addSbtPlugin("com.ossuminc" % "sbt-ossuminc" % "3.1.0")
addSbtPlugin("com.ossuminc" % "sbt-riddl" % "2.0.0-rc.9-29-989b7f46")
