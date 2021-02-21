const fs = require('fs');
const badChars = new Set(['#','<','>','*','_',':','\n','@']);
const badWords = new Set(['copyright','.com','www','copyediting','of fiction','e-book','all rights reserved','published by','publisher','manuscript','editor','coincidental','reproduce','special thank', 'inc.']);
const introductoryWords = new Set([/^(^|[^a-z0-9]*)introduction($|[^a-z0-9]*)$/gmi, /(^|[^a-z0-9]*)preface($|[^a-z0-9]*)$/gmi, /(^|[^a-z0-9]*)prologue($|[^a-z0-9]*)$/gmi, /(chapter|part|^)[^a-z0-9]*1([^a-z0-9]*|$)$/gmi, /(chapter|part|^)[^a-z0-9]*one([^a-z0-9]*|$)$/gmi, /(chapter|part|^)([^a-z0-9]*|^)i([^a-z0-9]*|$)$/gmi, /^([^a-z0-9]*)(1\.( )?)[a-z]*([^0-9]*|$)$/gmi]);

let removeUntilIntroduction = (text) => {
    let textByLines = text.split("\n");
    let lineCount = 0;
    let beginWordsDict = {};

    for (i in textByLines) {
        line = textByLines[i];
        if (line) {
            lineCount += 1;
            // line = line.map(x => toLowerCase(x));
            // console.log("line considered is: " + line);
        } else {
            continue;
        }

        if (lineCount >= 200) {
            break;
        }

        for (let word of introductoryWords) {
            // console.log("finding word: " + word);

            let search = line.match(word) || [];
            // console.log("search is: " + search);
            if (search.length > 0) {
                let rawMatch = search[0];

                // [^\w\s] is anything that's not a digit, letter, whitespace, or underscore.
                // [^\w\s]|_ is the same as ^ except including underscores.
                let match = rawMatch.replace(/[^\w\s]|_/g,"").toLowerCase().trim();

                // console.log("matching introductory word is: " + match);

                if (match in beginWordsDict) {
                    beginWordsDict[match].push(parseInt(i));
                } else {
                    beginWordsDict[match] = [parseInt(i)];
                }
                
                break;
            }
        }
    }

    console.log("beginWordsDict: " + JSON.stringify(beginWordsDict));

    // find a line number to read from
    let readFrom = 0;

    // if only one introductory word has appeared, start reading from that line
    if (Object.keys(beginWordsDict).length == 1) {
        let key = Object.keys(beginWordsDict)[0];
        // console.log("key is: " + key)
        // console.log("list being fed: " + beginWordsDict[key])
        readFrom = Math.max(...beginWordsDict[key]);
    } 
    // more than one introductory word has appeared
    else if (Object.keys(beginWordsDict).length > 1) {
        // all values (of key-value pairs) of the dictionary are single elem lists
        // i.e. multiple introductory words have appeared, but they all appear only once
        let allSingle = true;
        
        // all values (of key-value pairs) of the dictionary are multiple elem lists
        // i.e. multiple introductory words have appeared, but they all appear multiple times (usually twice)
        let allMulti = true;

        for (key in beginWordsDict) {
            if (beginWordsDict[key].length == 1) {
                allMulti = false;
            }  
            if (beginWordsDict[key].length > 1) {
                allSingle = false;
            }   
        }

        // this means there are keys with single elem lists AND ALSO keys with multiple elem lists
        // i.e. some introductory words appear once, some appeared more than once
        if (!allSingle && !allMulti) {
            for (key in beginWordsDict) {
                // only considering lists with 2 elements

                if (beginWordsDict[key].length == 2) {
                    // idea: start reading from the latest appearance of the earlier introductory word
                    // e.g. 
                    
                    // Contents Page
                    // -------------
                    // INTRODUCTION
                    // Chapter 1
                    // _____________
                    
                    // - actual book
                    // INTRODUCTION (start reading from here)

                    if (readFrom == 0) {
                        readFrom = Math.max(...beginWordsDict[key]);
                    } else {
                        readFrom = Math.min(...[Math.max(...beginWordsDict[key]), readFrom]);
                    }
                }

            }
        } 

        // all keys in dictionary have one elem lists
        else if (allSingle) {
            // idea: read the latest appearing introductory word
            // e.g.
                
            // Preface
            // Introduction
            // Chapter 1 (start reading from here)

            console.log("all keys in dictionary have one elem lists!");
            helper = []
            for (key in beginWordsDict) {
                helper.push(beginWordsDict[key]);
            }
            console.log("helper: " + helper);
            readFrom = Math.max(...helper);
        } 

        // all keys in dictionary have multiple elem lists
        else if (allMulti) {
            // idea: start reading from the latest appearance of the earlier introductory word
            // e.g. 
            
            // Contents Page
            // -------------
            //  INTRODUCTION
            //  Chapter 1
            //  _____________

            //  - actual book
            //  INTRODUCTION (start reading from here)
            //  Chapter 1

            helper = [];
            for (key in beginWordsDict) {
                helper.push(Math.max(...beginWordsDict[key]));
            }
            readFrom = Math.min(...helper);
        }  
    }   

    console.log("readFrom: " + readFrom);
    let newTextArray = textByLines.slice(readFrom);
    let newText = newTextArray.join("\n");
    return newText;
}

let getQuotes = (text) => {
    let quotes = [];
    let newText = removeUntilIntroduction(text)
    let paragraphs = newText.split("\n\n");
    // A quote is a paragraph with at least 10 words that doesnt include bad chars/words or thank you multiple times 
    for (i in paragraphs) {
        let par = paragraphs[i];
        let foundBadChar = false;
        let foundBadWord = false;

        for (j in par) {
            let char = par[j];
            if (badChars.has(char)) {
                foundBadChar = true;
                break;
            }
        }
        
        // let words = par.split().map(x => x.toLowerCase());
        // for (w in words) {
        //     let word = words[w];
        //     if (badWords.has(word)) {
        //         foundBadWord = true;
        //         break;
        //     }
        // }

        for (let badWord of badWords) {
            // let badWord = badWords[w];
            if (par.toLowerCase().includes(badWord)) {
                // console.log("par which has badWord is: " + par)
                // console.log("badWord is: " + badWord)
                console.log()
                foundBadWord = true;
                break;
            }
        }

        let thankYouCount = (par.split().map(x => x.toLowerCase()).join().match(/thank/gm) || []).length;
        let matches = par.match(/\w+/gm) || [];
        if (matches.length >= 10 && !foundBadWord && !foundBadChar && thankYouCount < 3) {
            quotes.push(par);
        }

    }

    return quotes;
}


let directory = "/Users/humuyao/Downloads/Book3";
let folders = ['7'];
var BreakException = {};

for (i in folders) {
    let subdir = directory + '/' + folders[i] + '/';
    fs.readdir(subdir, function (err, files) {
        if (err) console.error("Could not list the directory.", err);

        try {
            counter = 0
            files.forEach(function (filename, index) { 
                if (filename.endsWith(".txt")) {
                    counter += 1;
                    // console.log("book: " + filename)
                    let filePath = subdir + '/' + filename; 
                    
                    fs.readFile(filePath, 'utf8' , async function(err, text)  {
                        if (err) console.error(err);
                        console.log("book path: " + filename);
                        let quotes = getQuotes(text);
                        
                        for (count in quotes) {
                            // if (count > 10) {
                            //     break;
                            // }
                            let quote = quotes[count];
                            console.log("quote: " + JSON.stringify(quote));
                            
                        }
                        
                    });  
                }

                // console.log();
                if (counter == 4) {
                    throw BreakException;
                }
            });
        } catch (e) {
            if (e !== BreakException) throw e;
        }
    });
}