FROM node:22-alpine
WORKDIR /app
RUN corepack enable
COPY package.json ./
COPY prisma ./prisma
RUN pnpm install
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build
EXPOSE 4000
CMD ["pnpm", "start"]
