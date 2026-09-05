() => {
 const rows = Array.from(document.querySelectorAll('pre')).map((p,i) => {
  const root=p.closest('.rt-ScrollAreaRoot');
  const v=root.querySelector('[data-radix-scroll-area-viewport]');
  const bar=root.querySelector('.rt-ScrollAreaScrollbar');
  const thumb=root.querySelector('.rt-ScrollAreaThumb');
  const b=getComputedStyle(bar), t=thumb&&getComputedStyle(thumb);
  return {block:i+1,viewport:v.clientWidth,content:v.scrollWidth,overflow:v.scrollWidth-v.clientWidth,whiteSpace:getComputedStyle(p).whiteSpace,trackHeight:bar.getBoundingClientRect().height,thumbWidth:thumb?Math.round(thumb.getBoundingClientRect().width):0,thumbHeight:thumb?.getBoundingClientRect().height??0,visible:b.display!=='none'&&b.visibility==='visible'&&b.opacity==='1'&&(!thumb||(t.visibility==='visible'&&t.opacity==='1')),track:b.backgroundColor,thumb:t?.backgroundColor??null,scrollLeft:v.scrollLeft};
 });
 return {theme:document.querySelector('.radix-themes').className,width:innerWidth,pageOverflow:document.documentElement.scrollWidth-innerWidth,rows,inlinePadding:Array.from(new Set(Array.from(document.querySelectorAll('p code, li code')).map(c=>getComputedStyle(c).paddingRight)))};
}
