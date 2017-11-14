// helpers
var _ = require('lodash');
var log = require('../core/log.js');

// let's create our own method
var method = {};

method.init = function() {

    this.age = 0;

    this.currentTrend;
    this.requiredHistory = 16;

    //ADD_INDICATORS;

}

// what happens on every new candle?
method.update = function(candle) {

}


method.log = function() {

}



method.validation = function(ConditionList)
    {
       var validNB = ConditionList.filter(function(s) { return s.value; }).length;
       return validNB/ ConditionList.length; 
    }


method.check = function(candle) {




    //SIMPLIFY_INDICATORS;

    //BUYCONDITIONS;
    //SELLCONDITIONS;
 
    this.age++;
 

    if (this.validation(BuyConditions) > 0.1)
    {

        log.debug('we are currently in uptrend', message);

        if(this.currentTrend !== 'up') {
            this.currentTrend = 'up';
            this.advice('long');
        } else
            this.advice();

    }
    else if (this.validation(SellConditions) > 0.1)
    {


        if (this.currentTrend !== 'down') {
            this.currentTrend = 'down';
            this.advice('short');
        } else
            this.advice();

    } else {

        this.advice();
    }


}

module.exports = method;
