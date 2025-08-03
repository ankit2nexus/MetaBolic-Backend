import { Link } from "react-router-dom";
import pageImage from "../assets/page-not-found.svg";

function NotFoundPage() {
  return (
    <div className="w-full my-10 flex items-center justify-center flex-col text-center">
      <div className="w-64 mb-6">
        <img src={pageImage} alt="" />
      </div>
      <Link
        to="/"
        className="bg-violet-500 text-gray-100 font-semibold text-xl dark:bg-violet-700 dark:text-gray-100 px-3 py-1.5 rounded-full mt-4"
      >
        Go Home
      </Link>
    </div>
  );
}

export default NotFoundPage;
