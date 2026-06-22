import type { Project, ResearcherProfile, VerificationTask } from "./types.js"

export let projectsStore: Project[] = [
  {
    id: "proj-1",
    title: "High-Capacity Silicon-Graphene Composite Anode Battery",
    author: "MatDAO Energy Labs (Prof. Kenji Saito)",
    category: "Energy Storage",
    abstract:
      "A novel composite anode material combining high-purity silicon nanoparticles with a multi-layered graphene shell.",
    trl: 8,
    trlSummary:
      "Successfully integrated composite anodes into commercial-form-factor cylindrical cells and passed performance, abuse, and pre-production life cycle tests.",
    accomplishments: [
      "Synthesized silicon-graphene hybrid nanocomposites on scalable multi-gram fluid bed reactors.",
      "Assembled and validated coin-cell and pouch-cell prototypes (TRL 4-5).",
      "Completed rigorous environmental, safety, and cycle-life tests with external certification bodies (TRL 7).",
    ],
    potentialPartnership:
      "Seeking tier-1 automotive manufacturing partners for wide-scale tooling-up.",
    milestones: {
      prototype: {
        status: "completed",
        description: "Silicon nanoparticles enveloped in chemical vapor deposition graphene.",
        timeline: "Completed Q3 2024",
      },
      mvp: {
        status: "completed",
        description: "10Ah flexible pouch cells tested by industrial partners.",
        timeline: "Completed Q1 2025",
      },
      pilotTest: {
        status: "completed",
        description: "Continuous manufacturing trial at 200kg/month throughput.",
        timeline: "Completed Q1 2026",
      },
      commercialization: {
        status: "current",
        description: "Full automotive plant supply integration and safety certification.",
        timeline: "Target Q4 2026",
      },
    },
    score: 92,
    createdAt: new Date("2026-02-12T08:00:00Z").toISOString(),
    logo: "battery",
  },
  {
    id: "proj-2",
    title: "Metal-Organic Frameworks (MOFs) for Industrial Flue Carbon Capture",
    author: "CleanAir Consortium (Dr. Elena Rostova)",
    category: "Carbon Capture",
    abstract:
      "Specialized, highly porous copper-based copper-azolate frameworks designed to selectively adsorb CO2 from high-humidity coal and gas flue streams.",
    trl: 6,
    trlSummary:
      "Constructed a mock flue container side-vent assembly and successfully completed a continuous 480-hour carbon scrubbing trial.",
    accomplishments: [
      "Synthesized customized crystalline Cu-mof structures with low-cost precursor salts.",
      "Built and deployed a sub-scale flue chimney filter cartridge on active refinery gas outputs (TRL 6).",
    ],
    potentialPartnership:
      "Excellent prospect for clean tech energy funds, cement manufacturing companies, and oil & gas pipeline operators.",
    milestones: {
      prototype: {
        status: "completed",
        description: "High-affinity powder adsorption test at 1-liter gas chamber scale.",
        timeline: "Completed Q2 2025",
      },
      mvp: {
        status: "completed",
        description: "Extrudates loaded into a modular 10kg cart cartridge.",
        timeline: "Completed Q4 2025",
      },
      pilotTest: {
        status: "current",
        description: "Multi-cartridge slipstream reactor processing 1 ton of CO2 per day.",
        timeline: "In Progress, Target Q3 2026",
      },
      commercialization: {
        status: "future",
        description: "Wide-scale refinery integration and active carbon tax credit offset licensing.",
        timeline: "Target Q2 2027",
      },
    },
    score: 84,
    createdAt: new Date("2026-03-22T10:30:00Z").toISOString(),
    logo: "carbon",
  },
  {
    id: "proj-3",
    title: "AI-Driven Catalyst Discovery for Solid-State Electrolytes",
    author: "Tokyo Materials Institute (AI Core Team)",
    category: "AI Materials",
    abstract:
      "An end-to-end active learning pipeline that couples density functional theory simulation with neural-network crystallographic potential predictions.",
    trl: 4,
    trlSummary:
      "Completed active physical synthesis and atomic-scale microscopy validation of first ten AI-predicted compounds.",
    accomplishments: [
      "Trained custom Graph Neural Network models on 80,000 public and internal battery compositions.",
      "Synthesized high-purity crystalline powder samples of the top two candidate compounds (TRL 4).",
    ],
    potentialPartnership:
      "Seeking joint-development ventures with solid-state battery designers.",
    milestones: {
      prototype: {
        status: "current",
        description: "First solid pellet solid-state electrolyte assembly with lithium metal anodes.",
        timeline: "In Progress, Target Q4 2026",
      },
      mvp: {
        status: "future",
        description: "Multi-layer battery stack with >80% capacity retention over 100 cycles.",
        timeline: "Target Q2 2027",
      },
      pilotTest: {
        status: "future",
        description: "Integration with continuous roll-to-roll solid-state slot die coaters.",
        timeline: "Target Q1 2028",
      },
      commercialization: {
        status: "future",
        description: "Licensing chemistry formulations to solid electrolyte suppliers.",
        timeline: "Target Q4 2028",
      },
    },
    score: 76,
    createdAt: new Date("2026-04-05T14:20:00Z").toISOString(),
    logo: "ai",
  },
]

export let verificationStore: VerificationTask[] = [
  {
    id: "v-1",
    title: "Solvent-free high viscosity cathode slurry synthesis",
    milestoneName: "prototype",
    projectId: "proj-1",
    projectTitle: "High-Capacity Silicon-Graphene Composite Anode Battery",
    proofText:
      "We successfully formulated a high-solid content wet slurry for silicon anodes using a bio-derived chitosan binding agent. However, we used a temperature of -400°C to dry the foils.",
    submittedBy: "Prof. Kenji Saito",
    submittedAt: new Date("2026-06-08T10:15:00Z").toISOString(),
    aiPassed: false,
    aiPlagiarismScore: 12,
    aiConsistencyReport:
      "### CRITICAL TECHNICAL INCONSISTENCY\n\nTemperature of -400°C is physically impossible (absolute zero is -273.15°C).",
    humanVoted: false,
    status: "pending",
  },
]

export let researchersStore: ResearcherProfile[] = [
  {
    id: "res-1",
    name: "Dr. Alistair Vance",
    title: "Senior Synthesis Specialist",
    institution: "Imperial Metals Lab",
    skills: ["Solid-State Synthesis", "Precursor Crystallization", "Sintering Thermal Control"],
    bio: "Focused on clean synthesis routes for complex cobalt-free mineral structures.",
    synergyNeeds:
      "Seeking machine-learning developers to accelerate predictive grain alignment parameters on solid-solid battery junctions.",
    type: "academic",
  },
  {
    id: "res-2",
    name: "Cynthia Chen, PhD",
    title: "Materials Venture Catalyst",
    institution: "Anode Catalyst Ventures",
    skills: ["Venture Sourcing", "Scale Operations", "Automotive Casing Design"],
    bio: "Passionate about taking composite batteries from TRL 4 into direct industrial utility grids.",
    synergyNeeds:
      "Looking to partner with battery cathode chemical teams that have functional prototypes.",
    type: "entrepreneur",
  },
]
