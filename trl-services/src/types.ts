export interface Milestone {
  status: "completed" | "current" | "future"
  description: string
  timeline: string
}

export interface Project {
  id: string
  title: string
  author: string
  category: string
  abstract: string
  trl: number
  trlSummary: string
  accomplishments: string[]
  potentialPartnership: string
  milestones: {
    prototype: Milestone
    mvp: Milestone
    pilotTest: Milestone
    commercialization: Milestone
  }
  score: number
  createdAt: string
  logo: "battery" | "carbon" | "ai" | "chitin" | "shield" | "turbine" | "composite"
}

export interface ResearcherProfile {
  id: string
  name: string
  title: string
  institution: string
  skills: string[]
  bio: string
  synergyNeeds: string
  type: "academic" | "entrepreneur" | "engineer" | "investor"
}

export interface VerificationTask {
  id: string
  title: string
  milestoneName: string
  projectId: string
  projectTitle: string
  proofText: string
  submittedBy: string
  submittedAt: string
  aiPassed: boolean
  aiPlagiarismScore: number
  aiConsistencyReport: string
  humanVoted: boolean
  humanPassed?: boolean
  humanNotes?: string
  status: "pending" | "verified" | "rejected" | "flagged"
}
