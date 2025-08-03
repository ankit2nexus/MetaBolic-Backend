import { Calendar, ExternalLink, Tag, User } from "lucide-react";
import React from "react";

function NewsCard({ article }) {
  const { title, date, summary, url, tags, source:authors } = article || {};
  const formatDate = (dateString) => {
    const options = { year: "numeric", month: "short", day: "numeric" };
    return new Date(dateString).toLocaleDateString("en-us", options);
  };
  return (
    <div className="bg-white dark:bg-gray-900 dark:text-gray-100 p-4 rounded-lg shadow hover:shadow-md transition-shadow duration-300">
      <h2 className="text-xl font-semibold my-3 line-clamp-3">
        <a href={url} target="_blank">
          {title}
        </a>
      </h2>
      <div className="text-xs  flex flex-wrap items-center gap-4 mb-5">
        {authors && authors !== "Unknown" && (
          <div className=" flex items-center gap-2 text-gray-500 dark:text-gray-200">
            <span className="dark:bg-violet-700 rounded-full p-1.5"> <User size={16}  /></span>
            
            <span>{authors}</span>
          </div>
        )}
        {date && (
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-200">
            <span className="dark:bg-violet-700 rounded-full p-1.5"> <Calendar size={16} /></span>
            
            <span>{formatDate(date)}</span>
          </div>
        )}
      </div>
      <p className="text-gray-700 dark:text-gray-100 text-sm line-clamp-3 my-3">
        {summary}
      </p>
      {tags && tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {tags.map((tag, index) => (
            <div
              key={index}
              className="bg-violet-100 dark:bg-transparent text-violet-700 dark:text-violet-200 dark:border-2 dark:border-violet-600  text-xs font-semibold px-2 py-1 rounded-full flex items-center gap-1"
            >
              <Tag size={14} />
              <span>{tag.split("_").join(" ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default NewsCard;
