# Phase 1: Technology Decisions — Why Each Technology Was Chosen

## Backend

### FastAPI over Django/Flask
| Factor | FastAPI | Django | Flask |
|--------|---------|--------|-------|
| Performance | 5x faster (async) | Slower | Slower |
| Type Safety | Native Pydantic | Manual | Manual |
| Auto Docs | OpenAPI/Swagger built-in | DRF extension | Flask-RESTX |
| Async | Native | 4.0+ only | Not native |
| Learning Curve | Moderate | Steep | Easy |
| Ecosystem | Growing fast | Mature | Mature |

**Decision:** FastAPI for performance, type safety, and auto-generated API docs. Critical for a production app.

### PostgreSQL over MongoDB
| Factor | PostgreSQL | MongoDB |
|--------|-----------|---------|
| ACID | Full | Eventual consistency |
| JSONB | Yes (structured) | Native |
| Relationships | JOINs, constraints | Manual |
| pgvector | Yes (RAG) | Separate DB needed |
| Migrations | Alembic | Manual |
| Type Safety | Schema enforcement | Flexible but risky |

**Decision:** PostgreSQL for ACID compliance, relationships, and pgvector for RAG. MongoDB's flexibility is a liability for financial data.

### SQLAlchemy 2.0 over Raw SQL
| Factor | SQLAlchemy | Raw SQL |
|--------|-----------|---------|
| Type Safety | Mapped types | String queries |
| Relationships | Declarative | Manual JOINs |
| Migrations | Auto-generate | Manual |
| Security | Parameterized | Risk of injection |
| Productivity | High | Low |

**Decision:** SQLAlchemy for security, maintainability, and migration support.

### Redis over Memcached
| Factor | Redis | Memcached |
|--------|-------|-----------|
| Data Types | Strings, lists, sets, hashes | Strings only |
| Persistence | Optional | No |
| Pub/Sub | Yes | No |
| Lua Scripts | Yes | No |
| Memory Efficiency | Good | Better for simple caching |

**Decision:** Redis for rate limiting (sorted sets), session storage, and future WebSocket pub/sub.

---

## Frontend

### Next.js 15 over Vite/React
| Factor | Next.js | Vite+React |
|--------|---------|-----------|
| SSR/SSG | Built-in | Manual setup |
| Routing | App Router | react-router |
| i18n | Built-in | i18next setup |
| API Routes | Backend-for-frontend | Separate backend |
| Deployment | Vercel optimized | Manual |
| SEO | Automatic | Manual |

**Decision:** Next.js for SSR, i18n, and production deployment simplicity.

### TypeScript over JavaScript
| Factor | TypeScript | JavaScript |
|--------|-----------|-----------|
| Type Safety | Compile-time errors | Runtime errors |
| IDE Support | Auto-complete, refactoring | Basic |
| Maintainability | High (self-documenting) | Low |
| Team Scale | Better for teams | Solo OK |
| Migration Safety | Refactor with confidence | Risky |

**Decision:** TypeScript is non-negotiable for a production app. Catches bugs before they reach users.

### Tailwind CSS over CSS-in-JS/styled-components
| Factor | Tailwind | CSS-in-JS |
|--------|---------|-----------|
| Performance | Zero runtime | Runtime overhead |
| Bundle Size | Tree-shakeable | Adds to bundle |
| Consistency | Design system built-in | Manual consistency |
| Responsive | Utility classes | Media queries |
| Dark Mode | Built-in | Manual |

**Decision:** Tailwind for performance (zero runtime) and consistent design system.

### Zustand over Redux
| Factor | Zustand | Redux |
|--------|---------|-------|
| Boilerplate | Minimal | Lots |
| Bundle Size | 1KB | 11KB |
| TypeScript | Native | Good but verbose |
| Persistence | Built-in plugin | redux-persist |
| Learning Curve | Easy | Steep |

**Decision:** Zustand for simplicity. Redux is overkill for this app's state complexity.

### React Query over SWR
| Factor | React Query | SWR |
|--------|------------|-----|
| Features | Cache, mutation, pagination | Basic cache |
| DevTools | Excellent | Good |
| Mutations | First-class | Manual |
| Optimistic Updates | Built-in | Manual |
| Background Refetch | Configurable | Automatic |

**Decision:** React Query for comprehensive data fetching, caching, and mutation handling.

---

## AI/ML

### Ollama (Local) + OpenAI (Cloud) Hybrid
| Factor | Ollama | OpenAI |
|--------|--------|--------|
| Cost | Free | Pay per token |
| Privacy | Data stays local | Data sent to cloud |
| Quality | Good (Llama 3.1) | Excellent (GPT-4o) |
| Speed | Local inference | Network latency |
| Offline | Works | Requires internet |

**Decision:** Hybrid approach — Ollama for chat (free, private), OpenAI for vision (better accuracy for disease detection). Farmers have slow internet, so local-first is critical.

### pgvector over Pinecone/Weaviate
| Factor | pgvector | Pinecone | Weaviate |
|--------|----------|----------|----------|
| Infrastructure | Same PostgreSQL | Separate service | Separate service |
| Cost | Free | $70+/month | $25+/month |
| Latency | Same DB = fast | Network hop | Network hop |
| Maintenance | None extra | Managed | Managed |
| Features | Basic vector search | Advanced filters | Advanced filters |

**Decision:** pgvector for simplicity — no extra infrastructure, no extra cost, good enough for our use case.

### Whisper for STT
| Factor | Whisper | Google STT | Azure STT |
|--------|---------|-----------|-----------|
| Indian Languages | Excellent | Good | Good |
| Cost | $0.006/min | $0.006/min | $0.01/min |
| Offline | Yes (local model) | No | No |
| Quality | State-of-the-art | Good | Good |

**Decision:** Whisper for Indian language support and offline capability.

---

## Infrastructure

### Docker Compose over Kubernetes
| Factor | Docker Compose | Kubernetes |
|--------|---------------|------------|
| Complexity | Simple | Complex |
| Setup Time | Minutes | Hours/Days |
| Scaling | Manual | Auto-scaling |
| Production | Good for small/medium | Enterprise |
| Learning Curve | Easy | Steep |

**Decision:** Docker Compose for MVP and small-scale production. Migrate to ECS/Kubernetes when scaling beyond 10K users.

### Nginx over Traefik/Caddy
| Factor | Nginx | Traefik | Caddy |
|--------|-------|---------|-------|
| Maturity | 20+ years | 8 years | 6 years |
| Performance | Excellent | Good | Good |
| Config | Manual | Auto-discovery | Simple |
| Rate Limiting | Built-in | Plugin | Plugin |
| WebSocket | Excellent | Good | Good |

**Decision:** Nginx for battle-tested reliability, WebSocket support, and fine-grained rate limiting.

---

## Summary

Every technology was chosen for a specific reason:

1. **Performance** — FastAPI, Redis, pgvector, Tailwind
2. **Security** — JWT rotation, Pydantic validation, SQLAlchemy ORM
3. **Type Safety** — TypeScript, Pydantic, SQLAlchemy Mapped types
4. **Developer Experience** — Auto-generated docs, hot reload, great IDE support
5. **Cost** — Ollama (free), pgvector (free), Docker Compose (free)
6. **Farmer-Centric** — Voice-first, multilingual, offline-capable, low bandwidth
7. **Production-Ready** — Health checks, rate limiting, audit logging, security headers
