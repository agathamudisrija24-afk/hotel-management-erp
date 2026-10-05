/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'loremflickr.com' },
    ],
  },
  async rewrites() {
    const apiTarget = process.env.API_PROXY_TARGET || 'http://localhost:8000/api/v1';
    return [{ source: '/api/v1/:path*', destination: `${apiTarget}/:path*` }];
  },
};

module.exports = nextConfig;
