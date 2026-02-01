/*
 * Copyright 2026-2026 Ossum, Inc.
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

/** Validates all RIDDL files in the repository */
class RiddlValidationTest extends AnyWordSpec with Matchers:

  given PlatformContext = pc

  private val baseDir: File =
    // Get base directory from system property (set by sbt) or use current directory
    val path = sys.props.getOrElse("riddl.models.basedir", ".")
    new File(path)
  end baseDir

  /** Check if a file contains template placeholders that shouldn't be validated */
  private def isTemplateFile(file: File): Boolean =
    val source = Source.fromFile(file)
    try
      val content = source.mkString
      val placeholders = Seq(
        "{EntityName}",
        "{AggregateName}",
        "{SagaName}",
        "{RepositoryName}",
        "{ProjectorName}",
        "{ProcessName}",
        "{GatewayName}",
        "{ViewName}",
        "{ChildName}"
      )
      placeholders.exists(content.contains)
    finally
      source.close()
  end isTemplateFile

  /** Recursively find all .riddl files */
  private def findRiddlFiles(dir: File): Seq[File] =
    val files: Seq[File] = dir.listFiles() match
      case null => Seq.empty[File]
      case arr  => arr.toSeq

    files.filter(_.isFile).filter(_.getName.endsWith(".riddl")) ++
      files.filter(_.isDirectory).filterNot(_.getName.startsWith(".")).flatMap(findRiddlFiles)
  end findRiddlFiles

  /** Get relative path for display */
  private def relativePath(file: File): String =
    baseDir.toPath.relativize(file.toPath).toString

  "RIDDL models" should {

    val allRiddlFiles = findRiddlFiles(baseDir)
    val templatesToSkip = allRiddlFiles.filter(isTemplateFile)
    val filesToValidate = allRiddlFiles.filterNot(isTemplateFile)

    if templatesToSkip.nonEmpty then
      info(s"Skipping ${templatesToSkip.size} template file(s) with placeholders:")
      templatesToSkip.foreach(f => info(s"  - ${relativePath(f)}"))
    end if

    if filesToValidate.isEmpty then
      "have at least one non-template RIDDL file" in {
        info("No RIDDL files found to validate (templates are skipped)")
        succeed
      }
    else
      filesToValidate.foreach { file =>
        val path = relativePath(file)
        val absolutePath = file.getAbsolutePath

        s"validate $path" in {
          // Use RiddlParserInput.fromPath which handles absolute paths
          val rpiFuture = RiddlParserInput.fromPath(absolutePath)
          val rpi = Await.result(rpiFuture, 10.seconds)

          Riddl.parseAndValidate(rpi, shouldFailOnError = false) match
            case Left(messages) =>
              val errorMessages = messages.map(_.format).mkString("\n  ")
              fail(s"Parsing failed with ${messages.size} error(s):\n  $errorMessages")

            case Right(result) =>
              if result.messages.hasErrors then
                val errorMessages = result.messages.justErrors.map(_.format).mkString("\n  ")
                fail(s"Validation failed with ${result.messages.justErrors.size} error(s):\n  $errorMessages")
              else
                if result.messages.hasWarnings then
                  info(s"${result.messages.justWarnings.size} warning(s):")
                  result.messages.justWarnings.foreach(w => info(s"  ${w.format}"))
                end if
                succeed
              end if
          end match
        }
      }
    end if
  }
end RiddlValidationTest