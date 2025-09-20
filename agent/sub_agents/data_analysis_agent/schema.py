from pydantic import BaseModel, Field
from typing import List, Optional

# --- Define Output Schema for Startup Analysis ---

class StartupInfo(BaseModel):
    name: str = Field(description="Company name")
    tagline: str = Field(description="Company tagline or brief description")
    sector: str = Field(description="Industry sector")
    stage: str = Field(description="Funding stage (e.g., Seed, Series A, etc.)")
    founded: str = Field(description="Year founded")
    location: str = Field(description="Company location")
    employees: int = Field(description="Number of employees")
    website: str = Field(description="Company website")
    investmentScore: float = Field(description="Investment score (0-10 scale)")
    recommendation: str = Field(description="Investment recommendation")

class MetricValue(BaseModel):
    value: str = Field(description="Metric value")
    change: str = Field(description="Change from previous period")

class KeyMetrics(BaseModel):
    arr: MetricValue = Field(description="Annual Recurring Revenue")
    customers: MetricValue = Field(description="Customer count")
    runway: MetricValue = Field(description="Runway in months")
    cac: MetricValue = Field(description="Customer Acquisition Cost")

class CompetitorAnalysis(BaseModel):
    name: str = Field(description="Competitor company name")
    sector: str = Field(description="Competitor sector")
    funding: str = Field(description="Funding information")
    valuation: str = Field(description="Company valuation")
    arr: str = Field(description="Annual Recurring Revenue")
    growth: str = Field(description="Growth rate")
    employees: int = Field(description="Number of employees")
    strengths: List[str] = Field(description="Competitor strengths")
    weaknesses: List[str] = Field(description="Competitor weaknesses")

class RiskAssessment(BaseModel):
    type: str = Field(description="Risk type (Financial, Market, Technical, Regulatory)")
    issue: str = Field(description="Risk issue description")
    severity: str = Field(description="Risk severity (High, Medium, Low)")
    description: str = Field(description="Detailed risk description")
    evidence: str = Field(description="Evidence supporting the risk")
    mitigation: str = Field(description="Risk mitigation strategy")

class GrowthFactor(BaseModel):
    name: str = Field(description="Growth factor name")
    score: float = Field(description="Factor score (0-10)")
    weight: int = Field(description="Factor weight percentage")
    description: str = Field(description="Factor description")

class GrowthRecommendation(BaseModel):
    category: str = Field(description="Recommendation category")
    priority: str = Field(description="Priority level (High, Medium, Low)")
    title: str = Field(description="Recommendation title")
    description: str = Field(description="Recommendation description")
    impact: str = Field(description="Expected impact")
    timeline: str = Field(description="Implementation timeline")

class GrowthPotential(BaseModel):
    score: float = Field(description="Overall growth potential score")
    factors: List[GrowthFactor] = Field(description="Growth factors analysis")
    recommendations: List[GrowthRecommendation] = Field(description="Growth recommendations")

class RevenueBreakdown(BaseModel):
    month: str = Field(description="Month name")
    value: int = Field(description="Revenue value for the month")

class Revenue(BaseModel):
    current: str = Field(description="Current revenue")
    growth: str = Field(description="Revenue growth rate")
    projection: str = Field(description="Revenue projection")
    breakdown: List[RevenueBreakdown] = Field(description="Monthly revenue breakdown")

class FinancialMetric(BaseModel):
    label: str = Field(description="Metric label")
    value: str = Field(description="Metric value")
    change: str = Field(description="Change from previous period")
    positive: bool = Field(description="Whether change is positive")

class Funding(BaseModel):
    totalRaised: str = Field(description="Total funding raised")
    lastRound: str = Field(description="Last funding round")
    investors: List[str] = Field(description="List of investors")
    valuation: str = Field(description="Company valuation")

class FinancialData(BaseModel):
    revenue: Revenue = Field(description="Revenue information")
    metrics: List[FinancialMetric] = Field(description="Financial metrics")
    funding: Funding = Field(description="Funding information")

class Department(BaseModel):
    name: str = Field(description="Department name")
    count: int = Field(description="Number of employees in department")
    percentage: int = Field(description="Percentage of total employees")

class Leadership(BaseModel):
    name: str = Field(description="Leader name")
    role: str = Field(description="Leadership role")
    experience: str = Field(description="Years of experience")
    background: str = Field(description="Professional background")
    linkedin: str = Field(description="LinkedIn profile")

class Culture(BaseModel):
    satisfaction: str = Field(description="Employee satisfaction score")
    retention: str = Field(description="Employee retention rate")
    diversity: str = Field(description="Diversity metrics")

class TeamData(BaseModel):
    size: int = Field(description="Total team size")
    growth: str = Field(description="Team growth rate")
    departments: List[Department] = Field(description="Department breakdown")
    leadership: List[Leadership] = Field(description="Leadership team")
    culture: Culture = Field(description="Company culture metrics")

class MarketSize(BaseModel):
    tam: str = Field(description="Total Addressable Market")
    sam: str = Field(description="Serviceable Addressable Market")
    som: str = Field(description="Serviceable Obtainable Market")

class Competition(BaseModel):
    name: str = Field(description="Competitor name")
    marketShare: str = Field(description="Market share percentage")
    funding: str = Field(description="Funding amount")
    strength: str = Field(description="Key strength")

class Trend(BaseModel):
    trend: str = Field(description="Market trend")
    impact: str = Field(description="Impact level")
    timeline: str = Field(description="Timeline for trend")

class CustomerSegment(BaseModel):
    segment: str = Field(description="Customer segment name")
    percentage: int = Field(description="Percentage of revenue")
    revenue: str = Field(description="Revenue from segment")

class MarketData(BaseModel):
    size: MarketSize = Field(description="Market size metrics")
    competition: List[Competition] = Field(description="Competition analysis")
    trends: List[Trend] = Field(description="Market trends")
    customerSegments: List[CustomerSegment] = Field(description="Customer segments")

class Benchmark(BaseModel):
    metric: str = Field(description="Benchmark metric name")
    value: str = Field(description="Company value")
    benchmark: str = Field(description="Industry benchmark")
    status: str = Field(description="Performance status")

class AiSummary(BaseModel):
    investmentRecommendation: str = Field(description="Investment recommendation")
    confidenceScore: float = Field(description="Confidence score (0-10)")
    keyHighlights: List[str] = Field(description="Key investment highlights")
    mainConcerns: List[str] = Field(description="Main investment concerns")
    investmentThesis: str = Field(description="Investment thesis")
    nextSteps: List[str] = Field(description="Next steps for due diligence")

class Metadata(BaseModel):
    analysisId: str = Field(description="Unique analysis ID")
    analysisDate: str = Field(description="Analysis date")
    version: str = Field(description="Analysis version")
    processingTime: str = Field(description="Processing time")
    confidence: float = Field(description="Analysis confidence (0-1)")
    dataSource: str = Field(description="Data source")
    lastUpdated: str = Field(description="Last updated timestamp")

class StartupAnalysis(BaseModel):
    startup: StartupInfo = Field(description="Startup basic information")
    keyMetrics: KeyMetrics = Field(description="Key business metrics")
    competitorAnalysis: List[CompetitorAnalysis] = Field(description="Competitor analysis")
    riskAssessment: List[RiskAssessment] = Field(description="Risk assessment")
    growthPotential: GrowthPotential = Field(description="Growth potential analysis")
    financialData: FinancialData = Field(description="Financial data")
    teamData: TeamData = Field(description="Team information")
    marketData: MarketData = Field(description="Market data")
    benchmarks: List[Benchmark] = Field(description="Industry benchmarks")
    aiSummary: AiSummary = Field(description="AI analysis summary")
    metadata: Metadata = Field(description="Analysis metadata")
