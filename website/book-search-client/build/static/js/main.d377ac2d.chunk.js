(this["webpackJsonpbook-search-client"]=this["webpackJsonpbook-search-client"]||[]).push([[0],{122:function(e,t,a){"use strict";a.r(t);var r=a(0),n=a.n(r),o=a(10),c=a.n(o),s=(a(90),a(11)),i=(a(91),a(17)),l=a.n(i),u=a(13),h=a(22),j=a(177),b=a(183),d=a(124),g=a(167),m=a(182),p=a(184),O=a(12),x=a(170),f=a(174),v=a(173),y=a(172),k=a(175),T=a(4),C=a(176),S=a(72),w=a.n(S),B=a(57),N=a.n(B),R=a(70),q=a.n(R),F=a(3),P=Object(g.a)((function(e){return{root:{display:"flex",marginTop:"5%",marginBottom:"5%",border:"0.2em solid lightgrey"},cover:{maxWidth:120,minWidth:120,padding:7,objectFit:"cover"},details:{display:"flex",flexDirection:"column"},content:{},expand:{transform:"rotate(0deg)",marginLeft:"auto",transition:e.transitions.create("transform",{duration:e.transitions.duration.shortest})},expandOpen:{transform:"rotate(180deg)"}}}));function L(e){for(var t=e.resultObj,a=e.searchTerms,r=P(),o=n.a.useState(!1),c=Object(s.a)(o,2),i=c[0],l=c[1],u=t,h=t.quote?t.quote:"",j=(h.split(" "),""),b=0;b<u.authors.length;b++)b==u.authors.length-1?j+=u.authors[b]:j+=u.authors[b]+", ";return Object(F.jsxs)(x.a,{className:r.root,children:[Object(F.jsx)(y.a,{className:r.cover,children:Object(F.jsx)("img",{src:u.thumbnail,style:{"max-height":"100%","max-width":"100%",border:"0.2em solid black","border-radius":"0.1em"}})}),Object(F.jsxs)("div",{className:r.details,children:[Object(F.jsxs)(v.a,{className:r.content,children:[Object(F.jsx)(d.a,{variant:"h5",component:"h2",children:u.title}),Object(F.jsx)(d.a,{gutterBottom:!0,component:"h3",children:j}),Object(F.jsx)(d.a,{gutterBottom:!0,component:"h4",variant:"h6",style:{color:"darkblue","font-style":"italic"},children:h.length>300?Object(F.jsx)(q.a,{lines:3,more:"Show more",less:"Show less",className:"content-css",anchorClass:"my-anchor-css-class",expanded:!1,width:0,children:Object(F.jsx)("q",{cite:"https://www.mozilla.org/en-US/about/history/details/",children:Object(F.jsx)(N.a,{highlightClassName:"YourHighlightClass",searchWords:a,autoEscape:!0,textToHighlight:h})})}):Object(F.jsx)("q",{cite:"https://www.mozilla.org/en-US/about/history/details/",children:Object(F.jsx)(N.a,{highlightClassName:"YourHighlightClass",searchWords:a,autoEscape:!0,textToHighlight:h})})}),Object(F.jsx)(f.a,{disableRipple:!0,size:"small",color:"primary",href:u.previewLink,target:"_blank",style:{cursor:"pointer",textTransform:"none",backgroundColor:"transparent"},children:"View on Google Books"}),Object(F.jsx)("hr",{style:{color:"lightblue",align:"left",margin:0,width:"100%"}})]}),Object(F.jsx)(k.a,{className:Object(T.a)(r.expand,Object(O.a)({},r.expandOpen,i)),onClick:function(){l(!i)},"aria-expanded":i,"aria-label":"show more",children:Object(F.jsx)(w.a,{})}),Object(F.jsx)(C.a,{in:i,timeout:"auto",unmountOnExit:!0,children:Object(F.jsxs)(v.a,{children:[Object(F.jsx)(d.a,{gutterBottom:!0,variant:"h6",component:"h2",children:"Further Book Details"}),Object(F.jsxs)(d.a,{gutterBottom:!0,component:"h3",children:["\u2022 Book categories: ",u.categories]}),Object(F.jsxs)(d.a,{gutterBottom:!0,component:"h3",children:["\u2022 Number of pages: ",u.pageCount]}),Object(F.jsxs)(d.a,{gutterBottom:!0,component:"h3",children:["\u2022 Published date: ",u.publishedDate]}),Object(F.jsxs)(d.a,{gutterBottom:!0,component:"h3",children:["\u2022 ISBN: ",u["isbn-13"]]}),Object(F.jsxs)(d.a,{gutterBottom:!0,component:"h3",children:["\u2022 Average rating: ",""==u.averageRating?"":u.averageRating+"/5"]}),Object(F.jsxs)(d.a,{gutterBottom:!0,component:"h3",children:["\u2022 Number of ratings: ",u.ratingsCount]})]})})]})]})}var E=a(186);function W(e){var t=e.results,a=e.searchTerms,n=Object(r.useState)({data:[],searchTerms:[],offset:1,perPageResults:10}),o=Object(s.a)(n,2),c=o[0],i=o[1];console.log("Result page rendered"),Object(r.useEffect)((function(){(function(){var e=Object(h.a)(l.a.mark((function e(){return l.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:console.log("Use effect hook"),i(Object(u.a)(Object(u.a)({},c),{},{data:t,searchTerms:a}));case 2:case"end":return e.stop()}}),e)})));return function(){return e.apply(this,arguments)}})()()}),[]);var b,d=function(e){i(Object(u.a)(Object(u.a)({},c),{},{offset:e}))},g=Object.keys(c.data).length;return b=g%Number(c.perPageResults)==0?Math.floor(g/Number(c.perPageResults)):Math.floor(g/Number(c.perPageResults))+1,console.log("Page count",b),Object(F.jsx)(j.a,{container:!0,className:"book-container",spacing:6,justify:"center",alignItems:"center",children:Object(F.jsxs)(j.a,{item:!0,className:"book-card-result",xs:8,children:[g>c.perPageResults&&Object(F.jsx)(E.a,{count:b,page:c.offset,onChange:function(e,t){return d(t)}}),c.data.slice((c.offset-1)*c.perPageResults,(c.offset-1)*c.perPageResults+Number(c.perPageResults)).filter((function(e){return null!=e.title})).map((function(e,t){return Object(F.jsx)(L,{item:!0,resultObj:e,searchTerms:c.searchTerms},t)})),g>c.perPageResults&&Object(F.jsx)(E.a,{count:b,page:c.offset,onChange:function(e,t){return d(t)}})]})})}for(var I=a(55),_="https://ttds-14.herokuapp.com",D=function(){var e=Object(h.a)(l.a.mark((function e(t,a){return l.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return console.log("request endpoint",_+t),e.abrupt("return",I.post(_+t,{terms:a.terms,author:a.author,bookTitle:a.bookTitle,genre:a.genre,yearTo:a.yearTo,yearFrom:a.yearFrom,responseType:"json"}).then((function(e){return e.data})).catch((function(e){throw e})));case 2:case"end":return e.stop()}}),e)})));return function(t,a){return e.apply(this,arguments)}}(),G=a(189),H=a(187),M=a(178),Y=a(191),z=a(185),U=a(188),A=a(181),J=Object(g.a)((function(e){return{formControl:{margin:e.spacing(1),minWidth:120}}})),V=[],K=1990;K<2022;K++)V.push(K);function Q(e){var t=J(),a=Object(r.useState)({bookSearch:!1,author:"",bookTitle:"",genre:"",yearFrom:1990,yearTo:2021}),n=Object(s.a)(a,2),o=n[0],c=n[1],i=function(t,a){console.log("Field",t),console.log("Value",a),c(Object(u.a)(Object(u.a)({},o),{},Object(O.a)({},t,a))),e.handleChange(t,a)};return Object(F.jsxs)(F.Fragment,{children:[Object(F.jsx)(j.a,{container:!0,children:Object(F.jsx)(M.a,{control:Object(F.jsx)(H.a,{checked:o.bookSearch,onChange:function(e){return i("bookSearch",e.target.checked)},name:"bookSearch",color:"primary"}),label:"Book Search"})}),Object(F.jsxs)(j.a,{container:!0,spacing:1,children:[Object(F.jsxs)(j.a,{container:!0,item:!0,xs:12,spacing:3,children:[Object(F.jsx)(j.a,{container:!0,item:!0,xs:4,children:Object(F.jsx)(G.a,{id:"standard-basic",label:"Book Title",value:o.bookTitle,onChange:function(e){return i("bookTitle",e.target.value)}})}),Object(F.jsx)(j.a,{container:!0,item:!0,xs:4,children:Object(F.jsx)(G.a,{id:"standard-basic",label:"Author",value:o.author,onChange:function(e){return i("author",e.target.value)}})}),Object(F.jsx)(j.a,{container:!0,item:!0,xs:4,children:Object(F.jsx)(G.a,{id:"standard-basic",label:"Genre",value:o.genre,onChange:function(e){return i("genre",e.target.value)}})})]}),Object(F.jsxs)(j.a,{container:!0,item:!0,xs:12,spacing:3,children:[Object(F.jsx)(j.a,{container:!0,item:!0,xs:4,children:Object(F.jsxs)(A.a,{className:t.formControl,children:[Object(F.jsx)(U.a,{id:"year-from",children:"Year From"}),Object(F.jsx)(z.a,{labelId:"year-from-select",id:"year-from-select",value:o.yearFrom,onChange:function(e){return i("yearFrom",e.target.value)},children:V.map((function(e){return Object(F.jsx)(Y.a,{value:e,children:e},e)}))})]})}),Object(F.jsx)(j.a,{container:!0,item:!0,xs:4,children:Object(F.jsxs)(A.a,{className:t.formControl,children:[Object(F.jsx)(U.a,{id:"year-to",children:"Year To"}),Object(F.jsx)(z.a,{labelId:"year-to-select",id:"year-to-select",value:o.yearTo,onChange:function(e){return i("yearTo",e.target.value)},children:V.map((function(e){return Object(F.jsx)(Y.a,{value:e,children:e},e)}))})]})})]})]})]})}var X=Object(g.a)((function(e){return{heroContent:{backgroundColor:e.palette.background.paper,padding:e.spacing(8,0,6)},heroButtons:{marginTop:e.spacing(4)},margin:{margin:e.spacing(1)}}}));function Z(e){var t=X(),a=Object(r.useState)({quote:"",bookSearch:!1,author:"",bookTitle:"",genre:"",yearTo:2021,yearFrom:1990}),n=Object(s.a)(a,2),o=n[0],c=n[1];return Object(F.jsx)(F.Fragment,{children:Object(F.jsx)("div",{className:t.heroContent,children:Object(F.jsxs)(m.a,{maxWidth:"sm",children:[Object(F.jsx)(d.a,{component:"h1",variant:"h2",align:"center",color:"textPrimary",gutterBottom:!0,children:"Search a book by a quote"}),Object(F.jsx)(G.a,{fullWidth:!0,className:t.margin,label:"Type your quote...",multiline:!0,rowsMax:4,value:o.quote,onChange:function(e){c(Object(u.a)(Object(u.a)({},o),{},{quote:e.target.value}))}}),Object(F.jsx)(d.a,{variant:"h5",align:"center",color:"textSecondary",paragraph:!0,children:"Try to type something short and leading about the book you are looking for"}),Object(F.jsx)(Q,{handleChange:function(e,t){c(Object(u.a)(Object(u.a)({},o),{},Object(O.a)({},e,t))),console.log("Search features input:",e,t)}}),Object(F.jsx)("div",{className:t.heroButtons,children:Object(F.jsxs)(j.a,{container:!0,spacing:2,justify:"center",children:[Object(F.jsx)(j.a,{item:!0,children:Object(F.jsx)(f.a,{variant:"contained",color:"primary",onClick:function(){e.handleRequest(o)},children:"Submit"})}),Object(F.jsx)(j.a,{item:!0,children:Object(F.jsx)(f.a,{variant:"outlined",color:"primary",onClick:function(e){e.preventDefault(),c(Object(u.a)(Object(u.a)({},o),{},{quote:"",apiResponse:{},success:!1}))},children:"Clear"})})]})})]})})})}var $=Object(g.a)((function(e){return{icon:{marginRight:e.spacing(2)},cardGrid:{paddingTop:e.spacing(8),paddingBottom:e.spacing(8)},footer:{backgroundColor:e.palette.background.paper,padding:e.spacing(6)},margin:{margin:e.spacing(1)},formControl:{margin:e.spacing(1),minWidth:120}}}));function ee(){var e=$(),t=Object(r.useState)({apiResponse:{books:[]},searchTerms:[],isLoading:!1,requestError:"",success:!1}),a=Object(s.a)(t,2),o=a[0],c=a[1];console.log("Search page render");var i=function(){var e=Object(h.a)(l.a.mark((function e(t){var a,r,n,s,i,h,j,b;return l.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return a=t.quote,r=t.bookSearch,n=t.author,s=t.bookTitle,i=t.genre,h=t.yearFrom,j=t.yearTo,c(Object(u.a)(Object(u.a)({},o),{},{isLoading:!0,requestError:"",apiResponse:""})),console.log(o.isLoading),b=a.split(" "),e.next=6,D(r?"/books_from_terms_list":"/quotes_from_terms_list",{terms:b,author:n,bookTitle:s,genre:i,yearFrom:h,yearTo:j}).then((function(e){c(Object(u.a)(Object(u.a)({},o),{},{isLoading:!1,apiResponse:{books:e.books},requestError:"",success:!0,searchTerms:a.split(" ")}))})).catch((function(e){c(Object(u.a)(Object(u.a)({},o),{},{isLoading:!1,requestError:e,apiResponse:{quote:""}}))}));case 6:case"end":return e.stop()}}),e)})));return function(t){return e.apply(this,arguments)}}();return Object(F.jsxs)(n.a.Fragment,{children:[Object(F.jsx)(b.a,{}),Object(F.jsxs)("main",{children:[Object(F.jsx)(Z,{handleRequest:i}),Object(F.jsx)(m.a,{className:e.cardGrid,maxWidth:"md",children:o.isLoading?Object(F.jsx)(j.a,{container:!0,justify:"center",alignItems:"center",children:Object(F.jsx)(p.a,{})}):o.success&&Object(F.jsx)(W,{results:o.apiResponse.books,searchTerms:o.searchTerms})})]}),Object(F.jsxs)("footer",{className:e.footer,children:[Object(F.jsx)(d.a,{variant:"h6",align:"center",gutterBottom:!0,children:"Footer"}),Object(F.jsx)(d.a,{variant:"subtitle1",align:"center",color:"textSecondary",component:"p",children:"Something here to give the footer a purpose!"})]})]})}a(55),a(55);var te=function(){var e=Object(r.useState)({connectDB:{isLoading:!1,error:""}}),t=Object(s.a)(e,2);return t[0],t[1],Object(F.jsx)("div",{children:Object(F.jsx)(ee,{})})},ae=function(e){e&&e instanceof Function&&a.e(3).then(a.bind(null,192)).then((function(t){var a=t.getCLS,r=t.getFID,n=t.getFCP,o=t.getLCP,c=t.getTTFB;a(e),r(e),n(e),o(e),c(e)}))};c.a.render(Object(F.jsx)(n.a.StrictMode,{children:Object(F.jsx)(te,{})}),document.getElementById("root")),ae()},90:function(e,t,a){},91:function(e,t,a){}},[[122,1,2]]]);
//# sourceMappingURL=main.d377ac2d.chunk.js.map