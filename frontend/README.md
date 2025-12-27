# Metro İstanbul Agent - Frontend

Profesyonel, production-ready frontend application for Metro Istanbul AI Agent with multi-agent support, real-time features, and comprehensive admin panel.

## Features

### Chat Interface
- Real-time chat with Metro İstanbul AI Agent
- Voice input (Speech-to-text) with Turkish language support  
- Quick reply buttons for faster interaction
- Typing indicator animation
- Markdown support for formatted responses
- Fault report ID display and copy functionality
- Intent confidence visualization
- Session persistence (LocalStorage)

### Multi-Agent Architecture
- Extensible agent registry system
- Dynamic agent switching
- Agent-specific capabilities and intents
- Support for multiple AI agents

### Admin Panel
- **Dashboard**: Real-time metrics, statistics, charts
- **Fault Tracking**: Active faults list with filters
- **Analytics**: Intent distribution, response time trends
- **Agent Configuration**: Manage and configure agents

### UI/UX
- Dark/Light theme toggle
- Responsive design (mobile, tablet, desktop)
- Professional shadcn/ui components
- Smooth animations
- Toast notifications
- Loading states and skeletons
- Error handling with user-friendly messages

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Routing**: React Router 6
- **State Management**: Zustand (with persistence)
- **Data Fetching**: React Query (TanStack Query)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **API Client**: Axios
- **Icons**: Lucide React
- **Animations**: Framer Motion, Tailwind Animate
- **Markdown**: React Markdown
- **Notifications**: Sonner

## Installation

\`\`\`bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
\`\`\`

## Running the Application

### Development Mode

\`\`\`bash
npm run dev
\`\`\`

The application will start on [http://localhost:3000](http://localhost:3000)

### Production Build

\`\`\`bash
npm run build
npm run preview
\`\`\`

## Configuration

### Environment Variables

Create a \`.env\` file:

\`\`\`env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Metro İstanbul Agent
VITE_APP_VERSION=1.0.0
\`\`\`

### Backend Connection

Make sure the Metro Agent backend is running on \`http://localhost:8000\`:

\`\`\`bash
# In metro_agent directory
python main.py
\`\`\`

## Project Structure

\`\`\`
frontend/
├── src/
│   ├── api/              # API client & endpoints
│   ├── agents/           # Multi-agent architecture
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── chat/        # Chat interface
│   │   ├── admin/       # Admin panel
│   │   ├── layout/      # Layout components
│   │   └── common/      # Shared components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities & config
│   ├── pages/           # Page components
│   ├── store/           # Zustand stores
│   ├── styles/          # Global styles
│   └── utils/           # Helper functions
└── ...config files
\`\`\`

## Testing the Application

1. **Start Backend**:
   \`\`\`bash
   cd metro_agent
   python main.py
   \`\`\`

2. **Start Frontend**:
   \`\`\`bash
   cd frontend
   npm run dev
   \`\`\`

3. **Test Features**:
   - Navigate to [http://localhost:3000](http://localhost:3000)
   - Try sending messages in the chat
   - Test voice input (if browser supports)
   - Switch between light/dark themes
   - Visit admin panel at \`/admin\`

## API Integration

### Endpoints

- \`POST /message\` - Send chat message
- \`GET /health\` - Health check
- \`GET /service-status\` - Metro line statuses
- \`GET /faults\` - Active fault reports
- \`GET /lines\` - Metro lines
- \`GET /stations\` - Metro stations

## Troubleshooting

### Voice Input Not Working

- Check browser compatibility (Chrome, Edge recommended)
- Ensure microphone permissions are granted
- Voice input requires HTTPS in production

### Backend Connection Failed

- Verify backend is running on \`http://localhost:8000\`
- Check \`VITE_API_BASE_URL\` in \`.env\`
- Check CORS settings in backend

## License

This project is part of the Metro İstanbul Agent system.

---

**Built with ❤️ for Metro İstanbul**
