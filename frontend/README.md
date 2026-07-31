# Legacy System Health Monitor - Frontend

React frontend for the Legacy System Health Monitor dashboard.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API URL
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   ├── lib/            # Utilities and API client
│   ├── App.tsx         # Main application
│   └── main.tsx        # Entry point
├── public/             # Static assets
└── index.html          # HTML template
```

## Components

- **Dashboard**: Main dashboard layout with system selector
- **HealthGauge**: Circular gauge for health score visualization
- **MetricsPanel**: Real-time performance metrics display
- **AnomalyList**: List of detected anomalies with actions
- **SummaryPanel**: AI-generated system summary
- **MaintenancePanel**: Prioritized maintenance actions
- **KPITracker**: KPI progress tracking

## Features

- Real-time data updates with auto-refresh
- Interactive anomaly acknowledgment
- Maintenance action status tracking
- Responsive design with Tailwind CSS
- Type-safe with TypeScript
