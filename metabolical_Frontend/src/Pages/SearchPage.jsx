import React from "react";
import { useParams } from "react-router-dom";
import { useNews } from "../hooks/useNews";
import { getNewsBySearch } from "../utils/api";
import ErrorMessage from "../components/UI/ErrorMessage";
import Loading from "../components/UI/Loading";
import NewsGrid from "../components/UI/NewsGrid";

function SearchPage() {
  const { query } = useParams();

    const {
        data,
        isPending,
        error,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage,
      } = useNews("search", query, getNewsBySearch);
    const articles = data?.pages.flatMap((page) => page?.articles) || [];
    
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

export default SearchPage;
