import { CircleX } from "lucide-react";

function ErrorMessage({ error }) {
  return (
    <div className=" text-red-500 dark:text-red-700 font-semibold flex flex-col items-center my-12 gap-3">
        <div>
            <CircleX size={108} />
        </div>
      <span className="text-xl mb-3">Some error occured</span>
      <button onClick={() => window.location.reload()} className="text-white cursor-pointer bg-violet-500 dark:bg-violet-700 px-3 py-2 rounded-full">Try Again!</button>
    </div>
  );
}
export default ErrorMessage;