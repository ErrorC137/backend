import type { Project } from "./types.js"

export function parseStatus(status: string): "completed" | "current" | "future" {
  const s = status.toLowerCase()
  if (s.includes("completed") || s.includes("done")) return "completed"
  if (s.includes("current") || s.includes("progress")) return "current"
  return "future"
}

export function resolveLogo(
  category?: string,
): "battery" | "carbon" | "ai" | "chitin" | "shield" | "turbine" | "composite" {
  const categoryLower = (category || "").toLowerCase()
  if (categoryLower.includes("storage") || categoryLower.includes("battery")) return "battery"
  if (categoryLower.includes("carbon")) return "carbon"
  if (categoryLower.includes("ai") || categoryLower.includes("comput") || categoryLower.includes("learn"))
    return "ai"
  if (categoryLower.includes("bio") || categoryLower.includes("chitin")) return "chitin"
  if (categoryLower.includes("aero") || categoryLower.includes("turbine")) return "turbine"
  if (categoryLower.includes("secure") || categoryLower.includes("shield")) return "shield"
  return "composite"
}

export function generateFallbackProject(
  title: string,
  textContent: string,
  category?: string,
  author?: string,
): Project {
  let trl = 3
  if (/production|market|customer|licensed|factory|commercial|certified|faa/i.test(textContent + title)) {
    trl = 8
  } else if (/pilot|plant|refinery|environment|field test|operational/i.test(textContent + title)) {
    trl = 6
  } else if (/prototype|functional|assembly|working model|bench/i.test(textContent + title)) {
    trl = 4
  } else if (/theory|concept|simulated|modeling|formulate/i.test(textContent + title)) {
    trl = 2
  }

  const listAccomplishments: string[] = []
  if (trl >= 2) listAccomplishments.push(`Formulated basic research equations and molecular structures for ${title}.`)
  if (trl >= 3) listAccomplishments.push("Completed initial physical laboratory synthesis and bench test validations.")
  if (trl >= 5) listAccomplishments.push("Successfully validated functional prototype in operational mock chamber.")
  if (trl >= 7) listAccomplishments.push("Demonstrated system longevity and stability indexes under continuous load trial.")
  if (trl >= 8)
    listAccomplishments.push("Cleared validation and preliminary certifications with external deep-tech regulators.")

  const score = Math.min(99, Math.max(45, 40 + trl * 6 + Math.floor(Math.random() * 10)))
  const resolvedLogo = resolveLogo(category)

  return {
    id: "proj-" + Date.now(),
    title,
    author: author || "Independent Researcher",
    category: category || "Deep Tech",
    abstract: textContent.length > 250 ? textContent.substring(0, 250) + "..." : textContent,
    trl,
    trlSummary: `This project is classified as Technology Readiness Level ${trl}. The evaluation determined that key chemical compositions and mechanical baselines have been validated. Next stages require scaling fabrication parameters.`,
    accomplishments: listAccomplishments,
    potentialPartnership:
      trl >= 7
        ? "Strong outlook for scale-up joint fabrication. Seeking licensing deals with high-throughput manufacturer partners."
        : "Excellent fit for deep-tech venture seed funds, government research grants, and high-purity raw chemical suppliers.",
    milestones: {
      prototype: {
        status: trl >= 4 ? "completed" : "current",
        description: `Construct standalone functional cell arrays displaying target ${trl >= 4 ? "12% performance gain" : "initial specs"}.`,
        timeline: trl >= 4 ? "Completed Q2 2025" : "Target Q4 2026",
      },
      mvp: {
        status: trl >= 6 ? "completed" : trl >= 4 ? "current" : "future",
        description: "Assemble complete multi-layered stack packs validated for client preview slots.",
        timeline: trl >= 6 ? "Completed Q4 2025" : "Target Q2 2027",
      },
      pilotTest: {
        status: trl >= 8 ? "completed" : trl === 7 ? "current" : "future",
        description: "Deploy automated continuous trial processing loop in certified test environments.",
        timeline: trl >= 8 ? "Completed Q1 2026" : "Target Q1 2028",
      },
      commercialization: {
        status: trl === 9 ? "completed" : trl === 8 ? "current" : "future",
        description: "Enter full-scale OEM assembly lines, acquire safety approvals, and license proprietary formulations.",
        timeline: trl === 9 ? "Completed Q2 2026" : "Target Q4 2028",
      },
    },
    score,
    createdAt: new Date().toISOString(),
    logo: resolvedLogo,
  }
}

export function hasValidGeminiKey(): boolean {
  const key = process.env.GEMINI_API_KEY
  return Boolean(key && key !== "MY_GEMINI_API_KEY" && key.trim() !== "")
}
