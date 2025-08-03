import { useInfiniteQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const useNews = (keyName, keyValue, queryFn) => {
    const navigate = useNavigate();

  const query = useInfiniteQuery({
    queryKey: [keyName, keyValue],
    queryFn: ({ pageParam = 1 }) => queryFn(keyValue, pageParam),
    getNextPageParam: (lastPage) => {
      return lastPage?.has_next ? lastPage.page + 1 : undefined;
    },
    retry: 2,
    refetchOnWindowFocus: false,
  }, );

  useEffect(() => {
        if (query.error?.response?.status === 404) {
            navigate('/404');
        }
    }, [query.error, navigate]);

    return query;
};
