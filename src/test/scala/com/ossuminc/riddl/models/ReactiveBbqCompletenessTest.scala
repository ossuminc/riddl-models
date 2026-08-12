/*
 * Copyright 2026-2026 Ossum Inc.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package com.ossuminc.riddl.models

import com.ossuminc.riddl.language.parsing.RiddlParserInput
import com.ossuminc.riddl.passes.Riddl
import com.ossuminc.riddl.utils.{pc, Await, PlatformContext}
import org.scalatest.wordspec.AnyWordSpec
import org.scalatest.matchers.should.Matchers

import java.io.File
import scala.concurrent.duration.DurationInt
import scala.io.Source

/** Holds `reactive-bbq` to the rules in `docs/SIMULABILITY-AND-GENERATABILITY.md`.
  *
  * reactive-bbq is the reference model for Synapify simulation and riddlg code
  * generation, so it answers to more than "validates". Each rule here is
  * derived from an accepted item in `../RIDDL-Tools-To-Do-List.md` -- Part B is
  * riddlg, Part C is Synapify -- and the doc records which.
  *
  * Asserting the rules is deliberately preferred over running the tools. A
  * `riddlg gen` that exits 0 proves the generator did not crash; it does not
  * prove the model carried enough meaning to generate anything useful, it
  * cannot speak to simulability at all, and the most demanding generator
  * (Quarkus `gen code`) is Pro-gated and so cannot sit in an automated gate.
  *
  * This suite is EXPECTED TO FAIL when first added. It states the target; the
  * model is then brought up to it.
  */
class ReactiveBbqCompletenessTest extends AnyWordSpec with Matchers:

  given PlatformContext = pc

  private val baseDir: File =
    new File(sys.props.getOrElse("riddl.models.basedir", "."))

  private val modelDir: File =
    new File(baseDir, "hospitality/food-service/reactive-bbq")

  private val entryPoint: File = new File(modelDir, "reactive-bbq.riddl")

  /** Every `.riddl` making up the model, fragments included. */
  private def riddlFiles(dir: File): Seq[File] =
    val files = Option(dir.listFiles()).map(_.toSeq).getOrElse(Seq.empty)
    files.filter(f => f.isFile && f.getName.endsWith(".riddl")) ++
      files.filter(_.isDirectory).filterNot(_.getName.startsWith(".")).flatMap(riddlFiles)
  end riddlFiles

  private lazy val sources: Seq[(File, Seq[String])] =
    riddlFiles(modelDir).sortBy(_.getPath).map { f =>
      val s = Source.fromFile(f)
      try f -> s.getLines().toSeq
      finally s.close()
    }

  private def rel(f: File): String = baseDir.toPath.relativize(f.toPath).toString

  /** Every line of the model, tagged with where it came from. */
  private lazy val lines: Seq[(String, Int, String)] =
    sources.flatMap { case (f, ls) => ls.zipWithIndex.map { case (l, i) => (rel(f), i + 1, l) } }

  private def countMatching(re: scala.util.matching.Regex): Int =
    lines.count { case (_, _, l) => re.findFirstIn(l).isDefined }

  private def sitesMatching(re: scala.util.matching.Regex): Seq[String] =
    lines.collect { case (f, n, l) if re.findFirstIn(l).isDefined => s"$f:$n  ${l.trim}" }

  "reactive-bbq" should {

    "exist as the reference model" in {
      withClue(s"expected ${rel(entryPoint)} to exist: ") { entryPoint.exists() shouldBe true }
      sources should not be empty
    }

    // ---- R10: clean under the validator -------------------------------------

    "validate with zero errors and zero warnings (R10)" in {
      val loaded = Await.result(RiddlParserInput.fromPathSafe(entryPoint.getAbsolutePath), 30.seconds)
      val rpi = loaded match
        case Left(msgs)  => fail(s"could not read the model:\n  ${msgs.map(_.format).mkString("\n  ")}")
        case Right(in)   => in

      Riddl.parseAndValidate(rpi, shouldFailOnError = false) match
        case Left(msgs) => fail(s"parsing failed:\n  ${msgs.map(_.format).mkString("\n  ")}")
        case Right(result) =>
          val errors = result.messages.justErrors
          withClue(s"${errors.size} error(s):\n  ${errors.map(_.format).mkString("\n  ")}\n") {
            errors shouldBe empty
          }
          val warnings = result.messages.justWarnings
          withClue(s"${warnings.size} warning(s):\n  ${warnings.map(_.format).mkString("\n  ")}\n") {
            warnings shouldBe empty
          }
    }

    // ---- R1: no placeholders ------------------------------------------------

    "contain no `???` placeholder bodies (R1)" in {
      val sites = sitesMatching("""\?\?\?""".r)
      withClue(s"${sites.size} placeholder(s):\n  ${sites.mkString("\n  ")}\n") {
        sites shouldBe empty
      }
    }

    // ---- R2: brief AND description on every definition -----------------------

    "give every definition a full description, not only a brief (R2)" in {
      // A `briefly` with no `described` within the next few lines is a metadata
      // block that stopped half way.
      val orphans = sources.flatMap { case (f, ls) =>
        ls.zipWithIndex.collect {
          case (l, i)
              if l.trim.startsWith("briefly ") &&
                !ls.slice(i + 1, i + 4).exists(_.contains("described")) =>
            s"${rel(f)}:${i + 1}  ${l.trim}"
        }
      }
      withClue(s"${orphans.size} brief(s) with no description:\n  ${orphans.mkString("\n  ")}\n") {
        orphans shouldBe empty
      }
    }

    // ---- R3: a real glossary -------------------------------------------------

    "define the domain vocabulary as terms (R3)" in {
      val terms = countMatching("""^\s*term\s+\w+""".r)
      withClue(s"only $terms term(s) defined; Synapify surfaces these as hover-docs (Part C item 1) ") {
        terms should be >= 20
      }
    }

    // ---- R4: UI intent is modelled -------------------------------------------

    "express UI intent with groups and `put` statements (R4)" in {
      val groups = countMatching("""^\s*group\s+\w+""".r)
      val puts = countMatching("""^\s*put\s+""".r)
      withClue("riddlg's UI generator turns groups into a component tree (Part B item 4) ") {
        groups should be >= 4
      }
      withClue("outputs become subscriptions rendering results via `put` (Part B item 4) ") {
        puts should be > 0
      }
    }

    // ---- R5: epics are test specifications -----------------------------------

    "use every epic interaction block kind (R5)" in {
      // riddlg gives each a distinct test semantics: order, eventually, variants.
      val kinds = Map(
        "sequential" -> """^\s*sequence\b""".r,
        "parallel" -> """^\s*parallel\b""".r,
        "optional" -> """^\s*optional\b""".r
      )
      val missing = kinds.collect { case (name, re) if countMatching(re) == 0 => name }
      withClue(s"unused interaction block kinds: ${missing.mkString(", ")} ") {
        missing shouldBe empty
      }
    }

    "give every use case its own user story (R5)" in {
      // The case's user story becomes the generated scenario's narrative.
      val cases = sources.flatMap { case (f, ls) =>
        ls.zipWithIndex.collect {
          case (l, i) if l.trim.matches("""^case\s+\w+\s+is\s*\{.*""") =>
            val hasStory = ls.slice(i + 1, i + 4).exists(_.contains("wants to"))
            (s"${rel(f)}:${i + 1}  ${l.trim}", hasStory)
        }
      }
      val storyless = cases.filterNot(_._2).map(_._1)
      withClue(s"${storyless.size} use case(s) with no user story:\n  ${storyless.mkString("\n  ")}\n") {
        storyless shouldBe empty
      }
    }

    // ---- R9: versions exist so staleness is detectable ------------------------

    "carry a version so type-delta staleness can be detected (R9)" in {
      withClue("Synapify's git type-delta warning needs something to compare (Part C item 2) ") {
        countMatching("""^\s*version\s+""".r) should be > 0
      }
    }

    // ---- R12: canonical forms only -------------------------------------------

    "use no deprecated spellings (R12)" in {
      val deprecated = sitesMatching("""option\s+is\s+external""".r)
      withClue(s"deprecated forms found:\n  ${deprecated.mkString("\n  ")}\n") {
        deprecated shouldBe empty
      }
    }
  }
end ReactiveBbqCompletenessTest
