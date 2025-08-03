import { useNews } from "../hooks/useNews";
import Loading from "../components/UI/Loading";
import NewsGrid from "../components/UI/NewsGrid";
import ErrorMessage from "../components/UI/ErrorMessage";
import { getNewsByCategory } from "../utils/api";
function HomePage() { 
  const {
    data,
    isPending,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useNews("category", "news", getNewsByCategory);

  const articles = data?.pages.flatMap(page => page?.articles) || [];

  const handleLoadMore = () => {
    if (hasNextPage) fetchNextPage();
  };

  if (isPending) return <Loading />;
  if (error) return <ErrorMessage error={error} />;
  return (
    <NewsGrid
      articles={articles}
      onLoadMore={handleLoadMore}
      isFetchingMore={isFetchingNextPage}
      hasMore={hasNextPage}
    />
  );
}

export default HomePage;
