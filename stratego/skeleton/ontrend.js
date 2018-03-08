/*
  skeleton adapted from former strategy:

	RSI Bull and Bear + ADX modifier
	1. Use different RSI-strategies depending on a longer trend
	2. But modify this slighly if shorter BULL/BEAR is detected
	-
	12 feb 2017
	-
	(CC-BY-SA 4.0) Tommie Hansen
	https://creativecommons.org/licenses/by-sa/4.0/
*/

// req's
var log = require ('../../core/log.js');
var config = require ('../../core/util.js').getConfig();

// strategy
var strat = {
	
	/* INIT */
	init: function()
	{
		this.name = 'RSI Bull and Bear ADX';
		this.requiredHistory = 10//config.tradingAdvisor.historySize;
		this.resetTrend();
		
		// debug? set to flase to disable all logging/messages/stats (improves performance)
		this.debug = true;
		
		// performance
		//config.backtest.batchSize = 1000; // increase performance
		//config.silent = true;
		//config.debug = false;

      //JAPONICUS:BULLMOM|MOMENTUM,BEARMOM|MOMENTUM,SECMOM|MOMENTUM;

		// SMA
		this.addIndicator('maSlow', 'SMA', this.settings.SMA_long );
		this.addIndicator('maFast', 'SMA', this.settings.SMA_short );
		
		// RSI
	  this.addIndicator('BULL_momentum', 'BULLMOM', this.settings['BULLMOM'] );
		this.addIndicator('BEAR_momentum', 'BEARMOM', this.settings['BEARMOM'] );
		
		// ADX
		this.addIndicator('secondary_momentum', 'SECMOM', this.settings['SECMOM'] )
		
		
		// debug stuff
		this.startTime = new Date();
		
		// add min/max if debug
		if( this.debug ){
			this.stat = {
				adx: { min: 1000, max: 0 },
				bear: { min: 1000, max: 0 },
				bull: { min: 1000, max: 0 }
			};
		}
		
	}, // init()
	
	
	/* RESET TREND */
	resetTrend: function()
	{
		var trend = {
			duration: 0,
			direction: 'none',
			longPos: false,
		};
	
		this.trend = trend;
	},
	
	

	
	
	/* CHECK */
	check: function()
	{
		// get all indicators
		let ind = this.indicators,
			maSlow = ind.maSlow.result,
			maFast = ind.maFast.result,
			sec = this.indicators.secondary_momentum.result;
		
		
			
		// BEAR TREND
		if( maFast < maSlow )
		{
			var momentum = ind.BEAR_momentum.result;
			let momentum_hi = this.settings['BEARMOM'].thresholds.up,
				momentum_low = this.settings['BEARMOM'].thresholds.down;
			
			// ADX trend strength?
			if( sec > this.settings['SECMOM'].thresholds.up ) momentum_hi = momentum_hi + 15;
			else if( sec < this.settings['SECMOM'].thresholds.down ) momentum_low = momentum_low -5;
				
			if( momentum > momentum_hi ) this.short();
			else if( momentum < momentum_low ) this.long();
			

		}

		// BULL TREND
		else
		{
			var momentum = ind.BULL_momentum.result;
			let momentum_hi = this.settings['BULLMOM'].thresholds.up,
				momentum_low = this.settings['BULLMOM'].thresholds.down;

			// ADX trend strength?
			if( sec > this.settings['SECMOM'].thresholds.up ) momentum_hi = momentum_hi + 5;
			else if( sec < this.settings['SECMOM'].thresholds.down ) momentum_low = momentum_low -5;

			if( momentum > momentum_hi ) this.short();
			  else if( momentum < momentum_low )  this.long();
			
		}
		
		// add adx low/high if debug

	
	}, // check()
	
	
	/* LONG */
	long: function()
	{
		if( this.trend.direction !== 'up' ) // new trend? (only act on new trends)
		{
			this.resetTrend();
			this.trend.direction = 'up';
			this.advice('long');
			if( this.debug ) log.info('Going long');
		}
		
		if( this.debug )
		{
			this.trend.duration++;
			log.info('Long since', this.trend.duration, 'candle(s)');
		}
	},
	
	
	/* SHORT */
	short: function()
	{
		// new trend? (else do things)
		if( this.trend.direction !== 'down' )
		{
			this.resetTrend();
			this.trend.direction = 'down';
			this.advice('short');
			if( this.debug ) log.info('Going short');
		}
		
		if( this.debug )
		{
			this.trend.duration++;
			log.info('Short since', this.trend.duration, 'candle(s)');
		}
	},
	
	
	/* END backtest */
	end: function()
	{
		let seconds = ((new Date()- this.startTime)/1000),
			minutes = seconds/60,
			str;
			
		minutes < 1 ? str = seconds.toFixed(2) + ' seconds' : str = minutes.toFixed(2) + ' minutes';
		
		log.info('====================================');
		log.info('Finished in ' + str);
		log.info('====================================');
	
		// print stats and messages if debug
		if(this.debug)
		{
			let stat = this.stat;
			log.info('BEAR RSI low/high: ' + stat.bear.min + ' / ' + stat.bear.max);
			log.info('BULL RSI low/high: ' + stat.bull.min + ' / ' + stat.bull.max);
			log.info('ADX min/max: ' + stat.adx.min + ' / ' + stat.adx.max);
		}
		
	}
	
};

module.exports = strat;
