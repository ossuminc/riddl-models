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

/** Validates every model in the repository through the riddl library API.
  *
  * This is a second, independent path to the answer `sbt riddlcValidate` gives:
  * that one shells out to the riddlc binary, this one links the library and
  * calls `Riddl.parseAndValidate` in process. When the two disagree, the
  * disagreement is itself worth knowing.
  *
  * The unit is a MODEL, not a file. Most `.riddl` files here are `include`
  * fragments that begin at `context` or `entity` and cannot parse on their own;
  * only the file a `.conf` names in `input-file` is a whole model. Walking every
  * file instead -- which the first version of this suite did -- fails on some
  * 800 fragments that are not broken at all.
  *
  * The `patterns/` templates are out of scope for a further reason: they carry
  * `{Placeholder}` names and are fragments besides. `scripts/verify-templates.py`
  * covers those, and `sbt verifyTemplates` runs it.
  */
class RiddlValidationTest extends AnyWordSpec with Matchers:

  given PlatformContext = pc

  private val baseDir: File =
    val path = sys.props.getOrElse("riddl.models.basedir", ".")
    new File(path)
  end baseDir

  /** Every `.conf` file: one per model, by convention. */
  private def findConfFiles(dir: File): Seq[File] =
    val files: Seq[File] = dir.listFiles() match
      case null => Seq.empty[File]
      case arr  => arr.toSeq

    files.filter(_.isFile).filter(_.getName.endsWith(".conf")) ++
      files
        .filter(_.isDirectory)
        .filterNot(_.getName.startsWith("."))
        .filterNot(_.getName == "target")
        .flatMap(findConfFiles)
  end findConfFiles

  /** The model a `.conf` points at. `input-file` is relative to the `.conf`. */
  private def modelOf(conf: File): Option[File] =
    val source = Source.fromFile(conf)
    try
      val pattern = """input-file\s*=\s*"([^"]+)"""".r
      pattern.findFirstMatchIn(source.mkString).map { m =>
        new File(conf.getParentFile, m.group(1))
      }
    finally source.close()
  end modelOf

  private def relativePath(file: File): String =
    baseDir.toPath.relativize(file.toPath).toString

  "RIDDL models" should {

    val confs = findConfFiles(baseDir).sortBy(_.getPath)
    val models = confs.flatMap(c => modelOf(c).map(c -> _))

    if models.isEmpty then
      "find at least one model to validate" in {
        fail(s"no .conf with an input-file found under ${baseDir.getAbsolutePath}")
      }
    else
      models.foreach { case (conf, model) =>
        val path = relativePath(model)

        s"validate $path" in {
          if !model.exists() then
            fail(
              s"${relativePath(conf)} names input-file ${model.getName}, which does not exist"
            )
          end if

          // fromPathSafe rather than the deprecated fromPath: a file that
          // cannot be read should fail this test with its reason, not throw.
          val loaded =
            Await.result(RiddlParserInput.fromPathSafe(model.getAbsolutePath), 30.seconds)

          val rpi = loaded match
            case Left(messages) =>
              fail(
                s"Could not read $path:\n  " + messages.map(_.format).mkString("\n  ")
              )
            case Right(input) => input

          Riddl.parseAndValidate(rpi, shouldFailOnError = false) match
            case Left(messages) =>
              fail(
                s"Parsing failed with ${messages.size} error(s):\n  " +
                  messages.map(_.format).mkString("\n  ")
              )

            case Right(result) =>
              if result.messages.hasErrors then
                val errors = result.messages.justErrors
                fail(
                  s"Validation failed with ${errors.size} error(s):\n  " +
                    errors.map(_.format).mkString("\n  ")
                )
              else
                if result.messages.hasWarnings then
                  val warnings = result.messages.justWarnings
                  info(s"${warnings.size} warning(s):")
                  warnings.foreach(w => info(s"  ${w.format}"))
                end if
                succeed
              end if
          end match
        }
      }
    end if
  }
end RiddlValidationTest
