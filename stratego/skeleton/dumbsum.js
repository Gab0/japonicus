// helpers
var _ = require('lodash');
var log = require('../../core/log.js');

// let's create our own method
var method = {};

method.init = function() {

    this.age = 0;

    this.currentTrend;
    this.requiredHistory = 16;
    this.persistence=0;
    //ADD_INDICATORS;
    this.addindicator('inda', '..INDA..', this.settings['..INDA..'])
}

// what happens on every new candle?
method.update = function(candle) {

}


method.log = function() {

}



method.validation = function(ConditionList)
    {
       var validNB = ConditionList.filter(function(s) { return s; }).length;
       return validNB/ ConditionList.length; 
    }

method.checkPersistence = function(candidateAdvice)
{
    if (this.persistence >= this.settings.persistence)
        this.advice(candidateAdvice);
    else
        this.advice();

}

method.check = function(candle) {

    var price = candle.close;


    //SIMPLIFY_INDICATORS;

    //BUYCONDITIONS;
    //SELLCONDITIONS;
 
    this.age++;
 

    if (this.validation(BuyConditions) > 0.6)
    {

        if(this.currentTrend !== 'up') {
            this.currentTrend = 'up';
            this.advice();
            this.persistence=0;
        } else{
            this.persistence++;
            this.checkPersistence('long');

        }
    }
    else if (this.validation(SellConditions) > 0.6)
    {


        if (this.currentTrend !== 'down') {
            this.currentTrend = 'down';
            this.advice();
            this.persistence=0;
        } else{
            this.persistence++;
            this.checkPersistence('short');
        }


    } else {

        this.advice();
    }


}

module.exports = method;
