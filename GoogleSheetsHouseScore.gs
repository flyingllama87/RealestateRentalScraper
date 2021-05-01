/**
 * @OnlyCurrentDoc Limits the script to only accessing the current sheet.
 */

/**
 * A special function that runs when the spreadsheet is open, used to add a
 * custom menu to the spreadsheet.
 */
function onOpen() {
  var spreadsheet = SpreadsheetApp.getActive();
  var menuItems = [
    {name: 'Calculate Scores sheet...', functionName: 'calcScores'}
  ];
  spreadsheet.addMenu('House Tools', menuItems);
}


/*
Size (Above 600 - 1000 | 100 pts), under 600, -pts
Year Built (1970 - 2021 | 100 pts)
HouseSz (Above 120 - max 250 | 100 pts)
SUB_Location ( 0 - 5 | 200 pts)
PUB_Trans ( false / true | 50 pts)
Park ( false / true | 50 pts)
Btm_floor_legal (yes / no, 50 pts)
Final Price (below $600,000, start at $400,000, 100 pts), above 600 minus points
Num_Bath (1 - 4 | 0, 50, 100, 125 pts)
Qual (1 - 5 | 100 pts)
*/


// DATA, COLUMN
// SIZE, d
// YR_BUILT, e
// HOUSE_SZ, f
// EXTRA, g
// ACTION, h
// LOC_SCORE, i
// NEAR_PARK, j
// BEDROOMS, k
// BATHROOMS, l
// QUALITY, m
// NEAR_PUB_TRNSPRT, n
// POOL, o
// BTM_FLOOR_LGL, p
// COST, q
// FINAL_PRICE, r
// SCORE, s
// ADJUSTMENT, t


// Score magic
function calcScores() {
  var sheet = SpreadsheetApp.getActiveSheet();

  // var initialData = sheet.getRange('A2:Z2').getValues;
  var maxRowNum = 100;
  var curRowNum = 2;
  while(curRowNum < maxRowNum)
  {
    var sizeLoc = "D" + curRowNum.toString();
    var yearBuiltLoc = "E" + curRowNum.toString();
    var houseSizeLoc = "F" + curRowNum.toString();
    var suburbScoreLoc = "I" + curRowNum.toString();
    var parkProxLoc = "J" + curRowNum.toString();
    var bathCountLoc = "L" + curRowNum.toString();
    var qualityLoc = "M" + curRowNum.toString();
    var publicTransportProxLoc = "N" + curRowNum.toString();
    var bottomFloorLegalLoc = "P" + curRowNum.toString();
    var finalPriceLoc = "R" + curRowNum.toString();
    var scoreLoc = "S" + curRowNum.toString();
    var adjustmentLoc = "T" + curRowNum.toString();

    var size = sheet.getRange(sizeLoc).getValues();
    var yearBuilt = sheet.getRange(yearBuiltLoc).getValues();
    var houseSize = sheet.getRange(houseSizeLoc).getValues();
    var suburbScore = sheet.getRange(suburbScoreLoc).getValues();
    var parkProx = sheet.getRange(parkProxLoc).getValues();
    var bathCount = sheet.getRange(bathCountLoc).getValues();
    var quality = sheet.getRange(qualityLoc).getValues();
    var publicTransportProx = sheet.getRange(publicTransportProxLoc).getValues();
    var bottomFloorLegal = sheet.getRange(bottomFloorLegalLoc).getValues();
    var finalPrice = sheet.getRange(finalPriceLoc).getValues();
    var score = sheet.getRange(scoreLoc);
    var adjustment = Number(sheet.getRange(adjustmentLoc).getValue());

    if (yearBuilt >= 1970)
    {

      // normal range (0 to 100) between 600 and 1000 sqm.  Decrease advantage above 1000 and penalise below 600.
      var sizeScore = ((size - 600) / 400) * 100;
      if (sizeScore > 100)
      {
        sizeScore = ((sizeScore - 100) / 6) + 100;
      }
      else if (sizeScore < 0)
      {
        sizeScore = 0 - (Math.abs(sizeScore) * 2)
      }

      // 1970 to present
      var yearBuiltScore = (yearBuilt - 1970) * 2;
      
      // If built in the last 20 years, give 10 points score
      if (yearBuilt > 2000)
      {
        adjustment = adjustment + 10;
      }
      
      // normalise house size to 0-100 from 0 to 240 (should be 80 to 240?)
      var houseSizeScore = houseSize / 240 * 100;
      // Assume rebuild with 32 square version of https://plantationhomes.com.au/home-designs/retreat
      if (houseSize == 0)
      {
        houseSizeScore = 100;
      }

      // 20 Extra points for large houses (sqm)
      if (houseSize < 180)
      {
        adjustment = adjustment + 20;
      }

      // -10 points for small houses (sqm)
      if (houseSize < 120)
      {
        adjustment = adjustment - 20;
      }

      // 20 extra points for awesome suburb
      if (suburbScore == 5)
      {
        adjustment = adjustment + 20;
      }

      // penality for shitty suburb
      if (suburbScore == 1)
      {
        adjustment = adjustment - 40;
      }

      if (suburbScore == 0)
      {
        adjustment = adjustment - 500;
      }

      var suburbScoreScore = suburbScore * 40;

      // Close to park is dubious.  Should be a scale really.  Adjacent to a large park is different from being in walking distance from a small park
      var parkProxScore = 0;
      if (parkProx.includes("Y") > -1)
      {
        parkProxScore = 50;
      }


      var bathCountScore = 0;
      if (bathCount == 4)
      {
        bathCountScore = 125;
      }
      if (bathCount == 3)
      {
        bathCountScore = 100;
      }
      if (bathCount == 2)
      {
        bathCountScore = 75;
      }

      // Assume rebuild with 32 square version (2 bath) of https://plantationhomes.com.au/home-designs/retreat
      if (bathCount == 0)
      {
        bathCountScore = 100;
      }

      // Assume demolish and rebuild at quality of 1
      if (quality == 1)
      {
        quality = 6;
      }

      // Assume renovation on very poor quality
      if (quality == 2)
      {
        quality = 4;
      }

      // Assume average quality if missing
      if (quality == "")
      {
        quality = 3;
      }

      // 20 extra points for well presented places 
      if (quality > 4)
      {
        adjustment = adjustment + 20
      }

      var qualityScore = quality * 20;

      if (isNaN(adjustment))
      {
        adjustment = 0;
      }

      var publicTransportProxScore = 0;
      if (publicTransportProx.includes("Y") > -1)
      {
        publicTransportProxScore = 50;
      }
      
      var bottomFloorLegalScore = 0;
      if (bottomFloorLegal.includes("Y") > -1 || bottomFloorLegal.includes("N/A") > -1)
      {
        bottomFloorLegalScore = 50;
      }

      var finalPriceScore = (600000 - finalPrice) / 200000 * 200;

      if (finalPriceScore < 0)
      {
        finalPriceScore = 0 - (Math.abs(finalPriceScore) * 5);
      }

      // penalise expensive houses heavily
      if (finalPriceScore > 570000)
      {
        adjustment = adjustment - 50
      }
    
      var finalScore = sizeScore + 
          yearBuiltScore + 
          houseSizeScore + 
          suburbScoreScore + 
          parkProxScore + 
          bathCountScore +
          publicTransportProxScore + 
          bottomFloorLegalScore +
          finalPriceScore +
          adjustment;

        /*
          sizeScore, 100
          yearBuiltScore, 100 
          houseSizeScore, 100
          suburbScoreScore, 200
          parkProxScore, 50
          bathCountScore, 150
          publicTransportProxScore, 50 
          bottomFloorLegalScore, 50
          finalPriceScore, 200
        */
        var finalScoreMax = 100 + 100 + 100 + 200 + 50 + 150 + 50 + 50 + 200;

        score.setValue(
          Math.floor(finalScore).toString()
          // Math.floor(finalScore).toString() + "/" + finalScoreMax.toString()
        );
    }

  curRowNum++;
  }

  SpreadsheetApp.flush();

}
