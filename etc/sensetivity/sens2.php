<?php
$ncore = $_POST['ncore'];
$split = $_POST['split'];
$nremote = $_POST['nremote'];
$taper = $_POST['taper'];
$nintl = $_POST['nintl'];
$maxbl = $_POST['maxbl'];
$freq = $_POST['freq'];
$nsb = $_POST['nsb'];
$sbwidth = $_POST['sbwidth'];
$nchan = $_POST['nchan'];
$time = $_POST['time'];
$hms = $_POST['hms'];
$debug = $_POST['debug'];
?>

<html>
<head>
<title>LOFAR Image noise calculator (beta)</title>
<link href="sens.css" rel="stylesheet" type="text/css">
</head>

<!--
Image calculator v0.31, 10 August 2012
Written by George Heald (ASTRON)
-->

<!--
Form skeleton and css ideas from
http://24ways.org/2009/have-a-field-day-with-html5-forms/
-->

<body>

<h2>LOFAR Image noise calculator</h2>

<p>This calculator is in beta, so please use it with caution. It uses theoretical SEFD values, but these will be updated soon with empirical numbers. For information about the array and its capabilities please see the <a href="http://www.astron.nl/radio-observatory/astronomers/lofar-astronomers">LOFAR webpages at ASTRON</a>.</p>
<p>The calculations performed by this tool follow <a href="http://www.skatelescope.org/uploaded/59513_113_Memo_Nijboer.pdf">SKA Memo 113</a> by Nijboer, Pandey-Pommier, &amp; de Bruyn.</p>

<?php
if (!isset($_POST['submit'])){
?>
<form method=post action="<?php echo $_SERVER['PHP_SELF'];?>" id=calculator>
 <fieldset>
  <legend>Observation details</legend>
  <ul id=calclist>
   <li>
    <label for=ncore>Number of core stations (max 24)</label>
    <input id=ncore name=ncore type=number value=24 min=0 max=24 required autofocus>
    <ul><li>
    <label for=split>Split HBA core stations?</label>
    <input id=split name=split type=checkbox value=True>
    </li></ul>
   </li>
   <li>
    <label for=nremote>Number of remote stations (max 17)</label>
    <input id=nremote name=nremote type=number value=9 min=0 max=17 required>
    <ul><li>
    <label for=taper>Taper remote stations to 24 tiles?</label>
    <input id=taper name=taper type=checkbox value=True>
    </li></ul>
   </li>
   <li>
    <label for=nintl>Number of international stations (max 8)</label>
    <input id=nintl name=nintl type=number value=0 min=0 max=8 required>
   </li>
   <li>
    <label for=maxbl>Maximum baseline length (km)</label>
    <input id=maxbl name=maxbl type=number value=24 min=0.1 step=0.1 max=1500 required>
   </li>
   <li>
    <label for=freq>Observing frequency</label>
    <select id=freq name=freq>
     <option value="15">15 MHz (LBA_OUTER)</option>
     <option value="30">30 MHz (LBA_OUTER)</option>
     <option value="45">45 MHz (LBA_OUTER)</option>
     <option value="60">60 MHz (LBA_OUTER)</option>
     <option value="75">75 MHz (LBA_OUTER)</option>
     <option value="15I">15 MHz (LBA_INNER)</option>
     <option value="30I">30 MHz (LBA_INNER)</option>
     <option value="45I">45 MHz (LBA_INNER)</option>
     <option value="60I">60 MHz (LBA_INNER)</option>
     <option value="75I">75 MHz (LBA_INNER)</option>
     <option value="120">120 MHz</option>
     <option value="150" selected>150 MHz</option>
     <option value="180">180 MHz</option>
     <option value="200">200 MHz</option>
     <option value="210">210 MHz</option>
     <option value="240">240 MHz</option>
    </select>
   </li>
   <li>
    <label for=nsb>Number of subbands</label>
    <input id=nsb name=nsb type=number step=1 value=1 min=1 max=488 required>
   </li>
   <li>
    <label for=sbwidth>Subband width</label>
    <select id=sbwidth name=sbwidth>
     <option value="144042.96875">144 kHz (160 MHz clock)</option>
     <option value="180053.7109375" selected>180 kHz (200 MHz clock)</option>
    </select>
    <ul><li>
     <label for=nchan>Number of channels</label>
     <select id=nchan name=nchan>
      <option value="1">1 (use full bandwidth)</option>
      <option value="2">2</option>
      <option value="4">4</option>
      <option value="8">8</option>
      <option value="16">16</option>
      <option value="32">32</option>
      <option value="64" selected>64 (normal usage)</option>
      <option value="128">128</option>
      <option value="256">256 (max recommended)</option>
     </select>
    </li></ul>
   </li>
   <li>
    <label for=time>Integration time</label>
    <input id=time name=time type=number value=1 min=0.1 max=100000 step=0.1 required>
    <select id=hms name=hms>
     <option value="1">seconds</option>
     <option value="60">minutes</option>
     <option value="3600" selected>hours</option>
    </select>
   </li>
  </ul>
 </fieldset>
 <fieldset>
  <label for=debug>Debug mode?</label>
  <input id=debug name=debug type=checkbox value=True>
 </fieldset>
 <fieldset>
  <button type=submit value=submit name=submit>Calculate</button>
 </fieldset>
</form>

<?
} else {
 $coreminbl=array(91.935235,962.147561,547.051073,338.084900,526.353615,1337.936213,547.051073,123.603075,91.935235,337.805831,377.158862,262.782809,94.584484,115.106680,124.709665,539.212679,404.049359,328.300908,170.960453,262.045040,338.084900,523.436099,268.257269,526.353615);
 $remoteminbl=array(5729.541410,21099.638548,6258.421024,8654.204064,2324.647709,10596.283117,2324.647709,20020.281724,11504.534736,21975.406518,29978.367543,2332.769344,11504.534736,28448.229291,29978.367543,8654.204064,25083.536924);
 $intlminbl=array(495354.737837,53093.589869,554433.318337,53093.589869,280914.228715,188202.538750,491916.231352,188202.538750);
 $ncorein=24;
 $nremotein=17;
 $nintlin=8;
 foreach ($coreminbl as $cmbi) {
  if ($cmbi>$maxbl*1000) {
   $ncorein=$ncorein-1;
  }
 }
 foreach ($remoteminbl as $rmbi) {
  if ($rmbi>$maxbl*1000) {
   $nremotein=$nremotein-1;
  }
 }
 foreach ($intlminbl as $imbi) {
  if ($imbi>$maxbl*1000) {
   $nintlin=$nintlin-1;
  }
 }
 if ($ncorein < $ncore) {
  echo "<p><font color=red><b>Warning: Only ".$ncorein." core stations have minimum unprojected baseline lengths less than ".$maxbl." km, but you selected ".$ncore.".</b></font></p>";
 }
 if ($nremotein < $nremote) {
  echo "<p><font color=red><b>Warning: Only ".$nremotein." remote stations have minimum unprojected baseline lengths less than ".$maxbl." km, but you selected ".$nremote.".</b></font></p>";
 }
 if ($nintlin < $nintl) {
  echo "<p><font color=red><b>Warning: Only ".$nintlin." international stations have minimum unprojected baseline lengths less than ".$maxbl." km, but you selected ".$nintl.".</b></font></p>";
 }
 if ($freq>100 && $split=="True") {
  $nspl = $ncore * 2;
  echo "<p><font color=green><b>Using splitted HBA core stations, so that is ".$ncore."x2=".$nspl."</b></font></p>";
  $ncore = $nspl;
 }
 if ($freq>100 && $taper=="True") {
  echo "<p><font color=green><b>Using tapered HBA remote stations, so the calculator treats this as ".$ncore."+".$nremote." core stations and 0 remote stations</b></font></p>";
  $ncore = $ncore + $nremote;
  $nremote = 0;
 }
 $totalst = $ncore + $nremote + $nintl;
 if ($totalst > 64) {
  echo "<p><font color=red><b>Warning: Total number of stations (".$totalst.") exceeds maximum number that can be correlated (64).</b></font></p>";
 }
 $bandwidth = $nsb * $sbwidth / 1.e6;
 $sbwidthkhz = $sbwidth / 1.e3;
 $chwidth = $sbwidth / $nchan;
 $chwidthkhz = $chwidth / 1.e3;
 if ($freq>100) {
  $array = "HBA";
 } else if (substr($freq,-1)=="I") {
  $array = "LBA_INNER";
  $freq = substr($freq,0,-1);
 } else {
  $array = "LBA_OUTER";
 }
 $time = $time * $hms;
 echo "<p>Your inputs:";
 echo "<ul><li>Number of core stations = ".$ncore;
 echo "<li>Number of remote stations = ".$nremote;
 echo "<li>Number of international stations = ".$nintl;
 $nccbl = ($ncore * ($ncore - 1)) / 2;
 $nrrbl = ($nremote * ($nremote - 1)) / 2;
 $niibl = ($nintl * ($nintl - 1)) / 2;
 $ncrbl = ($ncore * $nremote);
 $ncibl = ($ncore * $nintl);
 $nribl = ($nremote * $nintl);
 $totalbl = $nccbl + $nrrbl + $niibl + $ncrbl + $ncibl + $nribl;
 echo "<li>Maximum baseline = ".$maxbl." km (used for confusion estimate)";
 echo "<li>Frequency = ".$freq." MHz (".$array.")";
 $timemin = $time / 60;
 $timehr = $timemin / 60;
 echo "<li>Time = ".$time." sec = ".$timemin." min = ".$timehr." hr";
 echo "<li>Bandwidth = ".$nsb." x ".$sbwidthkhz." kHz = ".$bandwidth." MHz";
 echo "<li>Number of channels = ".$nchan." (channel width = ".$chwidthkhz." kHz)</ul>";
 $sefdcore = array(
  "15I" => "2783900",
  "30I" => "211270",
  "45I" => "47560",
  "60I" => "31600",
  "75I" => "50950",
  "15" => "480170",
  "30" => "88760",
  "45" => "38160",
  "60" => "29590",
  "75" => "49330",
  "120" => "3570",
  "150" => "2820",
  "180" => "3230",
  "200" => "3520",
  "210" => "3660",
  "240" => "4060",
 );
 $sefdremote = array(
  "15I" => "2783900",
  "30I" => "211270",
  "45I" => "47560",
  "60I" => "31600",
  "75I" => "50950",
  "15" => "480170",
  "30" => "88760",
  "45" => "38160",
  "60" => "29590",
  "75" => "49330",
  "120" => "1790",
  "150" => "1410",
  "180" => "1620",
  "200" => "1760",
  "210" => "1830",
  "240" => "2030",
 );
 $sefdintl = array(
  "15I" => "518740",
  "30I" => "40820",
  "45I" => "18840",
  "60I" => "14760",
  "75I" => "24660",
  "15" => "518740",
  "30" => "40820",
  "45" => "18840",
  "60" => "14760",
  "75" => "24660",
  "120" => "890",
  "150" => "710",
  "180" => "810",
  "200" => "880",
  "210" => "920",
  "240" => "1020",
 );
 $prodcc = $sefdcore[$freq];
 $prodrr = $sefdremote[$freq];
 $prodii = $sefdintl[$freq];
 $prodcr = sqrt($sefdcore[$freq])*sqrt($sefdremote[$freq]);
 $prodci = sqrt($sefdcore[$freq])*sqrt($sefdintl[$freq]);
 $prodri = sqrt($sefdremote[$freq])*sqrt($sefdintl[$freq]);
 //$cc = $prodcc / sqrt($nccbl*2);
 //$rr = $prodrr / sqrt($nrrbl*2);
 //$ii = $prodii / sqrt($niibl*2);
 //$cr = $prodcr / sqrt($ncrbl*2);
 //$ci = $prodci / sqrt($ncibl*2);
 //$ri = $prodri / sqrt($nribl*2);
 //$sensall = sqrt(pow($cc,2)+pow($rr,2)+pow($ii,2)+pow($cr,2)+pow($ci,2)+pow($ri,2));
 //$imsens = $sensall / sqrt($bandwidth*$time*1.e6);
 $imsens = 1/sqrt(4*$bandwidth*$time*1.e6*($nccbl/pow($prodcc,2)+$nrrbl/pow($prodrr,2)+$niibl/pow($prodii,2)+$ncrbl/pow($prodcr,2)+$ncibl/pow($prodci,2)+$nribl/pow($prodri,2)));
 $chsens = 1/sqrt(4*$chwidth*$time*($nccbl/pow($prodcc,2)+$nrrbl/pow($prodrr,2)+$niibl/pow($prodii,2)+$ncrbl/pow($prodcr,2)+$ncibl/pow($prodci,2)+$nribl/pow($prodri,2)));
 $imsensmjy = 1000*$imsens;
 $chsensmjy = 1000*$chsens;
 $imsensujy = 1000000*$imsens;
 $chsensujy = 1000000*$chsens;
 $imsensstr = sprintf("%.2f",$imsens);
 $chsensstr = sprintf("%.2f",$chsens);
 $imsensmjystr = sprintf("%.2f",$imsensmjy);
 $chsensmjystr = sprintf("%.2f",$chsensmjy);
 $imsensujystr = sprintf("%.2f",$imsensujy);
 $chsensujystr = sprintf("%.2f",$chsensujy);
 $beam = 206265*((300/$freq)/(1000*$maxbl));
 $beamstr = sprintf("%.2f",$beam);
 $confjy = 0.000029*pow($beam,1.54)*pow(($freq/74.0),-0.7);
 $confmjy = 0.029*pow($beam,1.54)*pow(($freq/74.0),-0.7);
 $confujy = 29.0*pow($beam,1.54)*pow(($freq/74.0),-0.7);
 $confjystr = sprintf("%.2f",$confjy);
 $confmjystr = sprintf("%.2f",$confmjy);
 $confujystr = sprintf("%.2f",$confujy);
 if ($imsens > 1) {
  echo "<p><font color=green><b>Image sensitivity = ".$imsensstr." Jy/beam</b></font></p>";
 } else if ($imsensmjy > 1) {
  echo "<p><font color=green><b>Image sensitivity = ".$imsensmjystr." mJy/beam</b></font></p>";
 } else {
  echo "<p><font color=green><b>Image sensitivity = ".$imsensujystr." &mu;Jy/beam</b></font></p>";
 }
 if ($confjy > $imsens) {
  $confcolor = "red";
  $isnot = " ";
 } else {
  $confcolor = "green";
  $isnot = " not";
 }
 if ($confjy > 1) {
  echo "<p><font color=".$confcolor."><b>Confusion noise estimated as ".$confjystr." Jy/beam";
 } else if ($confmjy > 1) {
  echo "<p><font color=".$confcolor."><b>Confusion noise estimated as ".$confmjystr." mJy/beam";
 } else {
  echo "<p><font color=".$confcolor."><b>Confusion noise estimated as ".$confujystr." &mu;Jy/beam";
 }
 echo " (image will".$isnot." be confusion limited at ".$beamstr." arcsec resolution)</b></font></p>";
 if ($nchan > 1) {
  if ($chsens > 1) {
   echo "<p><font color=green><b>Sensitivity per channel = ".$chsensstr." Jy/beam</b></font></p>";
  } else if ($chsensmjy > 1) {
   echo "<p><font color=green><b>Sensitivity per channel = ".$chsensmjystr." mJy/beam</b></font></p>";
  } else {
   echo "<p><font color=green><b>Sensitivity per channel = ".$chsensujystr." &mu;Jy/beam</b></font></p>";
  }
 }
 echo "<p>Use your browser's &quot;Back&quot; button to change input settings.</p>";
 echo "Extra information:<ul>";
 echo "<li>Two polarizations are assumed.";
 echo "<li>An image weight parameter was not included but <i>may increase the calculated values</i> by a factor of 1.3-2.";
 echo "<li>No bandwidth losses due to RFI were assumed. This may be unrealistic. Typical band edges are excluded (amounting to keeping 59/64 channels). This is implicit in the subband bandwidths used here.</ul>";
 if ($debug=="True") {
  echo "<p>Debug info:<ul>";
  echo "<li>Number of core-core baselines = ".$nccbl." with effective SEFD ".$prodcc." Jy";
  echo "<li>Number of remote-remote baselines = ".$nrrbl." with effective SEFD ".$prodrr." Jy";
  echo "<li>Number of intl-intl baselines = ".$niibl." with effective SEFD ".$prodii." Jy";
  echo "<li>Number of core-remote baselines = ".$ncrbl." with effective SEFD ".$prodcr." Jy";
  echo "<li>Number of core-intl baselines = ".$ncibl." with effective SEFD ".$prodci." Jy";
  echo "<li>Number of remote-intl baselines = ".$nribl." with effective SEFD ".$prodri." Jy";
  echo "<li>Total number of baselines = ".$totalbl."</ul></p>";
 }
}
?>

<p id=logos><img src="LOFAR.png" height=40px>&nbsp;&nbsp;<img src="ASTRON.png" height=40px></p>
<p id=credit><i>Written by George Heald, v0.31 (10 August 2012)</i></p>
<div id=lofar><img src="lofarBWtrans_inv.png" width=350px></p>

</body>
</html>
