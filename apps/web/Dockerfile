FROM node:20-alpine AS builder
WORKDIR /repo
COPY package.json pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/contracts/package.json packages/contracts/package.json
RUN npm install
COPY apps/web apps/web
COPY packages/contracts packages/contracts
RUN npm run build --workspace @ap-civic/web

FROM node:20-alpine AS runner
WORKDIR /repo
ENV NODE_ENV=production
COPY --from=builder /repo/package.json /repo/package.json
COPY --from=builder /repo/apps/web /repo/apps/web
COPY --from=builder /repo/packages/contracts /repo/packages/contracts
COPY --from=builder /repo/node_modules /repo/node_modules
EXPOSE 3000
CMD ["npm", "run", "start", "--workspace", "@ap-civic/web"]
