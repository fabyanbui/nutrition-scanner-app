# Frontend & UI/UX Design Documentation

## System Aesthetic & Visual Design Philosophy

The **Nutrition Scanner** frontend (`apps/web`) is constructed with **Next.js App Router**, **TypeScript**, and **Tailwind CSS**.

### Aesthetic Principles
- **Clean High-Contrast Light Canvas**: Built on soft neutral slate tones (`#F8FAFC`, `#FFFFFF`) with crisp typography and distinct visual cards.
- **Vibrant Accent Palette**: Uses Emerald Green (`#059669`) for high confidence/health indicators, Warm Amber (`#D97706`) for calories/medium confidence, and Soft Rose (`#E11D48`) for warnings.
- **Generous Spacing & Hierarchy**: Employs mathematical padding ratios, subtle borders (`border-slate-200`), and layered cards with depth without glassmorphism noise.

---

## UI Component Hierarchy

```
+-------------------------------------------------------------------------------+
| App Layout (Header with Logo, App Title, Status Indicator)                   |
+-------------------------------------------------------------------------------+
|                                                                               |
|  Main Container (w-full max-w-6xl mx-auto)                                   |
|                                                                               |
|  +-----------------------------------+   +---------------------------------+  |
|  |  Left Column: Image Upload & Preview |   | Right Column: Real-time Analysis|  |
|  |                                   |   |                                 |  |
|  |  * Drag-and-Drop Dropzone Box    |   |  * Agent Progress Tracker       |  |
|  |  * File Input Button              |   |    - Food Recognition           |  |
|  |  * Selected Image Preview Card    |   |    - Ingredient Analysis        |  |
|  |  * Image Quality Guidance Banner  |   |    - Nutrition Estimation       |  |
|  |  * "Analyze Food" Button           |   |    - Quality Validation          |  |
|  |                                   |   |                                 |  |
|  |                                   |   |  * Detailed Analysis Results    |  |
|  |                                   |   |    - Detected Dishes Cards       |  |
|  |                                   |   |    - Key Macros Grid            |  |
|  |                                   |   |    - Ingredient Breakdown Table  |  |
|  |                                   |   |    - Quality Warnings Box       |  |
|  +-----------------------------------+   +---------------------------------+  |
|                                                                               |
+-------------------------------------------------------------------------------+
```

---

## State Management & Real-time Integration

### SSE Stream Consumer
The frontend page (`src/app/page.tsx`) uses standard browser `EventSource` to consume SSE streaming events:

```typescript
const eventSource = new EventSource(`/api/v1/analyze/${jobId}/stream`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.agent) {
    updateAgentState(data.agent, data.status, data.latency_ms);
  }
  
  if (data.status === "finished") {
    setResults(data.result);
    eventSource.close();
  }
};
```

### Dual-Layer API Strategy
1. **Primary Route**: Proxying requests to the FastAPI backend (`apps/api`) when running.
2. **Next.js Local Fallback (`apps/web/src/app/api/v1/`)**: If FastAPI is offline or uninstalled, Next.js API Route Handlers synthesize agent step streams locally so the frontend remains 100% interactive during client-only or serverless preview testing.

---

## Accessibility & Responsive Design

- **Mobile First Responsive Layout**: Uses Tailwind `grid-cols-1 lg:grid-cols-2` pattern to smoothly stack upload controls and analysis outputs on narrow screens.
- **Dynamic Touch Targets**: All interactive buttons maintain a minimum touch target height of **44px**.
- **WCAG AA Color Contrast**: All text pairings maintain a minimum contrast ratio of 4.5:1 against their card backgrounds.
