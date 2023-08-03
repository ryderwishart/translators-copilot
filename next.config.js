/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    return [
      {
        source: "/api/chat",
        destination: "/api/chat"
      },
      {
        source: "/api/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8080/api/:path*"
            : "/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
