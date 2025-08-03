import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
function SearchBar() {
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim() === "") return;
    navigate(`/search/${searchQuery}`);
    setSearchQuery("");
  };
  return (
    <form
      onSubmit={handleSearch}
      className="flex text-sm lg:text-base bg-gray-100 dark:bg-gray-700 dark:text-gray-50 items-center rounded-md overflow-hidden"
    >
      <input
        type="text"
        className=" px-3 py-2 flex-1  outline-none"
        onChange={(e) => setSearchQuery(e.target.value)}
        value={searchQuery}
        placeholder="search category, tags etc."
      />
      <button
        type="submit"
        className="bg-violet-500 dark:bg-violet-700 text-white p-3"
      >
        <Search size={18} strokeWidth={3} />
      </button>
    </form>
  );
}

export default SearchBar;
