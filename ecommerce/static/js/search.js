
      new Autocomplete('#autocomplete', {
          search: input => {
              const url = `/search/?search=${input}`
              return new Promise(resolve => {
                  fetch(url)
                      .then(response => response.json())
                      .then(data => {
                          resolve(data.payload)
                      })
              })
          },
          renderResult: (result, propes) => {
              
              let group = ''
              if (result.index % 3 == 0) {
                  group = `<li class="group" style="z-index:1;">Group<li>`
              }
              if (result.type == 'product') {
                  
                  return `
              ${group}
              <a class="wiki-title" href="/user/product/${result.id}" style="text-overflow: ellipsis; max-height: 1.5rem;overflow: hidden;">
                      <li ${propes} style="text-overflow: ellipsis; max-height: 3.5rem;overflow: hidden;">
                  ${result.textin}
                      
                      </li></a>`
              }
              if(result.type=='subcategory'){
                return `
              ${group}
              <li ${propes} style="text-overflow: ellipsis; max-height: 3.5rem;overflow: hidden;">
                  <a class="wiki-title" href="/search-result/${result.textin}" style="text-overflow: ellipsis; max-height: 1.5rem;overflow: hidden;">
                      ${result.textin} 
                      </a>
                      </li>`}
              if(result.type=='category'){
                return `
                ${group}
                <li ${propes} style="text-overflow: ellipsis; max-height: 3.5rem;overflow: hidden;">
                  <a class="wiki-title" href="/search-result/${result.textin}" style="text-overflow: ellipsis; max-height: 1.5rem;overflow: hidden;">
                      ${result.textin} 
                      </a>
                      </li>`
                }
          },getResultValue: result => result.textin
      })