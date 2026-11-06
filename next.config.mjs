/** @type {import('next').NextConfig} */
const isGithubPages = process.env.GITHUB_PAGES === "true";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig = {
  ...(isGithubPages ? { output: "export" } : {}),
  basePath,
  images: { unoptimized: true },
};

export default nextConfig;
