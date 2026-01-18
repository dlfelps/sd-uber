# Product Guidelines

## Communication Style
- **Educational & Transparent:** Every part of the system should serve as a learning resource. Documentation, API responses, and code comments must explain *why* certain decisions were made, not just *what* the code does.
- **Informative Error Handling:** API errors must be more than just status codes. They should provide clear, actionable feedback to help developers understand the system's state and correct their requests.

## Development Principles
- **Clarity Over Cleverness:** We prioritize readable, idiomatic code. Complex optimizations should only be introduced when they are essential for the core "low-latency matching" requirement and must be accompanied by a detailed explanation.
- **Embedded Context:** Architectural decisions and technical trade-offs should be documented as close to the code as possible (e.g., in module-level READMEs or block comments) to ensure the rationale is always available.
- **Deep-Dive Summaries:** Task completions and Git summaries should include a brief analysis of the implementation, referencing the `design.md` to reinforce the connection between requirements and code.

## Visual & Structural Standards
- **API-First Design:** Since the project is developer-focused, the "UI" is the API. Responses should be structured logically, use consistent naming conventions, and be fully self-describing where possible.
- **Modular Architecture:** The system should be broken down into clear, distinct services as outlined in the architecture, making it easier for learners to isolate and understand individual components.
