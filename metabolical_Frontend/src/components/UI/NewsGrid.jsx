import React, { useRef } from "react";
import NewsCard from "./NewsCard";
import noDataFoundImg from "../../assets/data-not-found.svg";

function NewsGrid({ articles, onLoadMore, isFetchingMore, hasMore }) {
  const scrollRef = useRef(null);
  return (
    <>{
      articles && articles.length === 0 && <div className="flex text-center text-gray-500 font-semibold text-xl justify-center items-center flex-col py-12 w-full">
        <div className=" py-4 w-52 lg:w-64">
          <img src={noDataFoundImg} alt="no data found" />
        </div>
        <span>No Article found</span>
      </div>
    }
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles &&
          articles.length > 0 &&
          articles.filter(article => article !== undefined || null ).map((article, index) => (
            <NewsCard key={index} article={article} />
          ))}
      </div>
      {hasMore && articles.length > 0 &&(
        <div className="text-center mt-6">
          <button
            className="mt-4 px-4 py-2 bg-violet-500 dark:bg-violet-700 text-white rounded-full hover:bg-violet-800"
            onClick={onLoadMore}
          >
            Load More
          </button>
        </div>
      )}
    </>
  );
}

export default React.memo(NewsGrid);
