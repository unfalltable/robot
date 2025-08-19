import { useEffect } from 'react';
import { useRouter } from 'next/router';

const Home = () => {
  const router = useRouter();

  useEffect(() => {
    // 自动重定向到仪表盘
    router.replace('/dashboard');
  }, [router]);

  return null;
};

export default Home;
