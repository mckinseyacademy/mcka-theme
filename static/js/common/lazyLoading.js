LazyLoading = {
	initialize: function(url, collection, listOfLazyFields, queryParamsDict, loadingIdentifier)
	{
		this.options.url = url;
		this.options.collection = collection;
		this.options.listOfLazyFields = listOfLazyFields;		
		if (queryParamsDict)
			this.options.queryParamsDict = queryParamsDict;
		if (loadingIdentifier)
			this.options.loadingIdentifier = loadingIdentifier;
	},
	options: {
		loadingIdentifier:'.',
		modelComparisonId:'id',
		url:'',
		collection:{},
		listOfLazyFields:[],
		queryParamsDict:{},
		modelCheckupTime: 100,
		modelLocksDictionary:{}
	},
	modelProtection:function(){
		var intervalId = setInterval(function(){
			for (key in modelLocksDictionary)
			{
				if (modelLocksDictionary[key])
				{
					return 0;
				}
			}
		
		},this.options.modelCheckupTime)
	}
}