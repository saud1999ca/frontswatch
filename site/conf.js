/* Yemen: everything about this conflict that the app would otherwise hardcode.
   Each conflict ships one of these next to its data.js, geo.js and ar.js. */
const CONF={
 id:'yemen',
 start:'2014-09-21',
 unit:'governorate',            /* what an admin area is called here */
 homeKey:'yemen',               /* which BOX is 'the country' view */
 /* an event outside this envelope widens the auto view to the region */
 homeBounds:{latMax:20.2,lonMin:40.3,lonMax:56},
 box:{yemen:[11.3,19.8,41.2,55.6],region:[11.3,27.3,37.6,57.2]},
 names:{saada:'Saada',amran:'Amran',capital:'Sanaa City',sanaa:'Sanaa Governorate',hajjah:'Hajjah',mahwit:'Al Mahwit',hodeidah:'Hodeidah',raymah:'Raymah',dhamar:'Dhamar',ibb:'Ibb',bayda:'Al Bayda',jawf:'Al Jawf',marib:'Marib',taiz:'Taiz',lahij:'Lahij',aden:'Aden',dhale:'Ad Dhale',abyan:'Abyan',shabwa:'Shabwa',hadramawt:'Hadramawt',mahrah:'Al Mahrah',socotra:'Socotra'},
 short:{capital:'',sanaa:'',amran:'',mahwit:'',raymah:'',aden:'',dhale:'Dhale',bayda:'Bayda',mahrah:'Mahrah'},
 who:{H:'Houthis',G:'Government',S:'STC',A:'AQAP'},
 act:{H:'Houthis',G:'Government',C:'Saudi-led coalition',S:'STC',A:'AQAP',U:'Unclear'},
 /* quick zoom targets under the map */
 focus:[{ll:[13.58,44.02],i:'f_taiz',en:'Taiz'},
        {ll:[15.46,45.33],i:'f_marib',en:'Marib'},
        {ll:[14.2,43.3],i:'f_red',en:'Red Sea'},
        {ll:[12.9,45.0],i:'f_aden',en:'Aden'}]
};
