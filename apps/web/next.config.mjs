/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';
    return [
      {
        source: '/api/v1/evaluations/:path*',
        destination: `${apiUrl}/api/v1/evaluations/:path*`,
      },
      {
        source: '/api/v1/evaluations',
        destination: `${apiUrl}/api/v1/evaluations`,
      },
    ];
  },
};

export default nextConfig;
