const List = ({ listTitles }) => {
    
    return (
        <div>
            {
                listTitles.map((clustor) => (
                    <div className="flex-start">
                    <div className="p-6 max-w-xs bg-white rounded-lg border border-gray-200 shadow-md dark:bg-white-400 dark:border-white-700 m-auto mb-4 gap-y-4 dark:hover:bg-gray-100">
    <a href={`/clustors/${clustor.address}/`}>
        <h5 className="mb-2 text-2xl font-semibold tracking-tight text-gray-800">{ clustor.cname }</h5>
        <a className="inline-flex items-center text-blue-600 hover:underline" href={`/clustors/${clustor.address}/`}>
        Interact
        <svg className="ml-2 w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"></path><path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"></path></svg>
    </a>
    </a>
</div>
</div>
                    ))
            } 
        </div>
    );
};

export default List;



