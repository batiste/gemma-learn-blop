
## Import syntax

### Grammar

```javascript
import %name% from %file%
import { %name%[ as %rename%]?[, %name%[ as %rename%]?]* } from %file%
import %file% as %name%
import %file%
```

### Examples

```javascript
import Index from './index.blop'
import { createRouter, createRoute as something } from './routing.blop'
import 'webpack-dev-middleware' as middleware
import 'express'
```

## Variables creation and assignment

Variable are simply declared Python style. Variables are hoisted at the top of the current block scope and will all be compiled as `let` variables.

```javascript
index = 1
{ x, y, z as depth } = { x: 1, y: 2, z: 100.0 }
depth = index       // reassigning a variable will trigger an error
depth := depth + 1  // to avoid the error use the explicit reassign operator :=
```

## Function syntax

### Grammar

```javascript
async? def %name%? (%parameters%)[:%annotation%]? { %statements% }
async? (%parameters%)[:%annotation%]? => { %statements% }
async? (%parameters%)[:%annotation%]? => %expression%
```

### Examples

```javascript
def greet(name='John Doe'): string {
  return `Hello `name`` 
}
async def memePageHandler(params, state) {
  return fetch('http://example.com/api')
}
(a, b): number => a + b
pow = (a) => a * a
```

## Loop syntax

```javascript
for %value% in %expression%[:%annotation%]? { %statements% }
for %key%, %value% in %expression%[:%annotation%]? { %statements% }
while %expression% { %statements% }
```

### Examples

```javascript
petList = ['cat', 'dog', 'goldfish']

for pet in petList {
  console.log(pet)
}
// the array annotation indicate that Object.keys doesn't need to be used on petList 
for index, dog in petList: array {
  console.log(dog, index)
}
while true {
  console.log('infinite loop')
}
```

## Condition syntax

### Grammar

```javascript
if %expression% { %statements% }
if %expression% { %statements% } else { %statements% }
if %expression% { %statements% } elseif %expression% { %statements% }
if %expression% { %statements% } elseif %expression% { %statements% } else { %statements% }
```

### Examples

```javascript
def index(state) {
  if state.page == 'dog' {
    <DogPage state=state></DogPage>
  } elseif state.page == 'meme' {
    <MemePage state=state></MemePage>
  } else {
    <span>'No pages'</span>
  }
}
```
## Strings

Strings can be delimited with ", ', or ` and are all functionally equivalent. String concatenation
is achieved by simply sticking the string together around an expression.

```javascript
whitespace = " "
console.log('hello'whitespace`world`) // output hello world
```

## Other structure

Try catch, object literal, array literal, classes, object creation, regular expressions, errors, object destructuring, are all equivalent or similar to ES6

```javascript
class ExampleClass {
  def constructor(something=false) {
    this.routes = [1, 2, 3]
    this.state = { hello: 1, world: 2 }
  }
  async def dangerous(id) {
    try {
      response = await fetch(`https://heloo`id``)
      response.data.replace(/abc/g, 'cdf')
    } catch e {
      console.log(e)
      throw new Error('API failure')
    }
  }
}
```

## Virtual DOM statements

### Grammar

```javascript
<name[%attributes%]*/>
<name[%attributes%]*>%statements%</name>
<name[%attributes%]*>%expression%</name>
```

With %attributes% being

```javascript
%whitespaces% %name%=%expression%
%whitespaces% %name%
```

### Examples

Virtual DOM statements need to be declared inside a function. A function with a virtual
DOM statement will automatically return a virtual DOM tree when executed. There should only be a single root virtual DOM statement by function that contains all the children. The root virtual node
generates a return statement therefor the code that comes after it will never be executed.

```javascript
def button(label) {
  <div class="col">
    <button class="btn" on={ click: alert("oki") }>label</button>
  </div>
  // any code after this point will not be executed.
}
```

You are allowed to have several virtual DOM root in a function if you use conditionals

```javascript
def index(state) {
  if state.page == 'dog' {
    <span>'DOG'</span>
  } else {
    <span>'CATS'</span>
  }
}
```

You can output string nodes, or other virtual node by using the assignment syntax _=_.
You can also assign virtual DOM to variables. In this case they are not statements anymore and
can be declared outside of a function scope.

```javascript
cat = <img src="cat.png"/> // this is a virtual DOM expression

def button(name) {
  <button class="btn">
    = cat
    = "Our nice button is named: "
    = name
  </button>
}
```

You can mix any statements of the language inside your virtual nodes (conditional, loops, other functions, other virtual nodes functions)

```javascript
def button(number) {
  <button class="btn">
    if number > 100 {
      = "Big number "
    } else {
      [1, 2, 3].forEach(
        (index) => <span>'small number'</span>)
    }
  </button>
}
```

### Virtual DOM Components

A component is simply a function with a special signature. It will receive all its attributes as a first parameter (object), and all its children as a second parameter (list).
For a function to be recognised by _blop_ as a component you need to capitalise its name.

[More specific information about Component](https://github.com/batiste/blop-language/wiki/Components)

```javascript
def Button(attributes, children) {
  <button class=attributes.class>children</button>
}

Link = (attributes, children) => <a href=attributes.href>children</a>

def index(state) {
  href = 'http://www.google.com'
  <div>
    <Button class='btn'>'Index page'</Button>
    <Link href>'google.com'</Link>
  </div>
}
```

You could have used _Button_ as a function and it would completely equivalent

```javascript
def index(state) {
  <div>
    = Button({ class: 'btn' }, ['Index page'])
  </div>
}
```

### Virtual DOM Event

Events on Virtual DOM can be used by using the _on_ attribute

```javascript
def ChangeInput(attributes, children) {
  { change, value, label } = attributes
  // virtual nodes can be assigned to variables
  input = <input
    on={ change: (event) => change(event, input.elm) }
    type="text" value />
  <label>
    = label
    = input
  </label>
}

def index(state) {
  label = 'url'
  value = 'http://example.com'
  change = (event, dom) => {
    console.log(event.target.value, dom.value) // 2 equivalent ways to get the changed value
  }
  <ChangeInput label value change></ChangeInput>
}
```

### Virtual DOM Hooks

Blop uses the snabbdom hooks https://github.com/snabbdom/snabbdom#hooks that allows you to deal
with the lifecycle of your application.
Those hooks can be attached to any virtual DOM node. However they cannot be attached to a component as those are just functions.
To attache lifecycle elements events to component you should use [Component Lifecycle
](https://github.com/batiste/blop-language/wiki/Components#component-lifecycle)

```javascript
def FocusedInput(attributes, children) {
  hooks = {
    insert: (vnode) => {
      vnode.elm.focus()
      vnode.elm.select()
    }
  }
  <label>
    = children
    = ': '
    <input hooks
      type="text" value=attributes.value />
  </label>
}

def InputPage(attributes) {
  <div>
    <FocusedInput value="something">'Your name'</FocusedInput>
  </div>
}
```






