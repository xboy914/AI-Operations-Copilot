const stages = ["Request received", "Agent planning", "Tool execution", "Human approval", "Audit complete"];
export default function Home() {
  return <main>
    <header><span className="eyebrow">AGENTIC OPERATIONS</span><h1>AI Operations<br/><em>Copilot</em></h1><p>Auditable workflows with human control at every critical boundary.</p></header>
    <section className="panel"><div><span className="live">● API FOUNDATION</span><h2>Workflow control plane</h2></div><button>Create workflow</button></section>
    <section className="grid">{stages.map((stage, index)=><article key={stage}><small>0{index+1}</small><h3>{stage}</h3><p>{index===3 ? "Explicit approval required" : "Observable and traceable"}</p></article>)}</section>
  </main>;
}
