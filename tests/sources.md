# Reverse Engineering Sources

Each image beside this file is a render of the prompt below it. Keeping the prompts is what
makes the corpus a test: a reconstruction can be read against what the image was actually
built from, rather than only against what it looks like.

The first seven were written for this corpus and rendered through `krea2-api.json` at seed 1,
one per medium. The five after them are the author's own work, picked from a library of
several hundred to cover media the first seven never reach — a screen-print poster, an
orthographic elevation, an isometric render, a natural history plate and a flat gouache
illustration. Their prompts are recovered from the ComfyUI graph in each PNG, so the ground
truth is exact there too, and they were made with the same checkpoint at eight steps, differing
only in seed. Being written without this corpus in mind, they are the harder half: none was
composed to be reconstructible.

They are renders rather than scans or photographs, which keeps the licence clean and the
ground truth exact, and makes them easier than a real source would be.

`photograph.png` serves twice: as a reconstruction source, and as the image the critique case
is asked to judge. Its faults are the point there — a lower third of wet asphalt holding a
reflection too diffuse to read, and a figure whose shoes meet the kerb line almost exactly.

## photograph.png

```
Style: a documentary photograph on 35mm colour film with visible grain, available light, a restrained palette, plain and observational.
A man in a dark wool coat stands under a bus shelter on the right of the frame, facing left, his hands in his coat pockets and his collar turned up. The shelter's glass side panel is scratched and smeared, and reflects a grey street behind him. Wet asphalt fills the lower third of the frame, holding a long reflection of the shelter's frame. A red and white bus sign is mounted high at the left edge, and a bare plane tree stands behind the shelter.
```

## portrait.png

```
Style: an oil portrait in the manner of the Spanish Baroque, thin glazes over a dark ground, restricted to earth colours and lead white, grave and still.
A bearded man is seen in three-quarter view from the chest up, turned to the right of the frame with his eyes meeting the viewer. He fills the central third from the shoulders to just below the top edge, which crops the crown of his head. He wears a plain black doublet with a narrow white collar, and his hands are not visible. The ground behind him is an unbroken warm brown, lit slightly behind his right shoulder, and a single raking light falls across his face from the upper left.
```

## drawing.png

```
Style: a sumi ink brush drawing on absorbent paper, black ink in three dilutions and nothing else, spare and deliberate.
A single pear stands upright slightly left of centre in the frame, its outline drawn in one continuous loaded stroke that thickens along the right flank. Its stem leans to the right. A second, paler wash marks a shadow pooling to the left of the base. The remainder of the paper is left bare, and a small red seal sits in the lower right corner.
```

## engraving.png

```
Style: a copperplate engraving with dense cross-hatching, ink on cream paper, no colour at all, crowded and industrious.
A market square seen from slightly above, packed with figures. In the foreground a woman weighs fish at a trestle table on the left, while two men argue over a barrel on the right, one gesturing with an open hand. Behind them a line of eleven stalls with striped awnings recedes toward the middle distance, hung with poultry, bread and bolts of cloth. Beyond the stalls a church front with a rose window and two lancet doors closes the upper third of the frame. Dogs move between the legs of the crowd, and a cart with a broken wheel is tipped against the left edge.
```

## geometric.png

```
Style: a hard-edge geometric abstraction in flat opaque paint, the color held to four values with no blending, precise and impersonal.
A grid of twelve equal squares, three across and four down, fills the frame edge to edge with thin white gutters of even width between them. Each square holds one filled circle centred within it, reaching two thirds of the square's width. The circles run vermilion, black, pale grey and vermilion again across each row, so no two circles of the same colour touch. The ground behind the gutters is a flat warm white.
```

## abstract.png

```
Style: an abstract expressionist oil painting with loaded palette-knife strokes and visible ridges, a palette of black, cadmium red and bone white only, violent and unresolved.
Three broad strokes cross the frame on a steep diagonal from the lower left to the upper right, the widest of them black and running the full width. A dense mass of cadmium red gathers in the upper left quarter, scraped thin at its lower edge where it meets bare white ground. Bone white is dragged across the lower right corner in short broken passes. Nothing in the field resolves into an object, and the paint stands proud of the surface throughout.
```

## collage.png

```
Style: a mixed-media collage of torn newsprint, gouache and pencil on board, a limited palette of ochre, black and faded blue, restless and provisional.
A human head in profile faces left in the upper half of the frame, its silhouette torn from newsprint whose columns of type run vertically and whose edges are ragged and fibrous. Below it a band of faded blue gouache crosses the full width of the frame, brushed unevenly so the board shows through in places. Three pencil circles overlap at the lower right, drawn in visible graphite lines that cross each other. A strip of ochre paper is pasted along the bottom edge, its corner lifting away from the board.
```

## poster.png

```
Style: a mid-century modern travel-poster illustration in screen-print style, flat bold geometric color blocking, a weathered halftone grain texture over every surface, warm sunlit tones set boldly against cool tones, rhythmic and bold in mood.
A large circle dominates the upper two-thirds of the frame, its center offset slightly left of the vertical midline so open cream space breathes along the right edge. The circle splits into four quadrants: upper-left in deep vermillion red, upper-right and lower-right in golden mustard yellow, and lower-left in tight concentric rings alternating deep red and black. A small solid navy-blue circle sits exactly where the four quadrants converge, anchoring the composition's optical center. Thin vertical black stripes on a pale cream ground show through the negative space framing the circle's upper edge, giving the top of the frame a taut, structured backdrop. Below, a second, smaller circular motif of golden yellow and burnt orange concentric rings sits right of center, its lower half submerged in horizontal bands of teal blue wave ripples that span the full width of the lower third, creating a stable horizontal base beneath the circular forms above. In the lower-left corner, a smaller red concentric semicircle breaks the wave bands, echoing the large circle's curve and balancing the golden motif on the opposite side. The layered horizontals of the waves contrast with the stacked verticals behind the sun, while the two circular motifs, offset in size and position along a shared diagonal, lead the eye from upper-left down to lower-right through the ripple patterns.
```

## elevation.png

```
Style: Flat orthographic elevation architecture rendering, 2D front-facing view with zero perspective distortion, clean vector-style linework, muted flat color fills with minimal shading, thin uniform outline weight, blueprint-adjacent technical illustration aesthetic, subtle line-hatching for texture only, restrained color palette, crisp edges, flat layered silhouettes with no depth cues

Mid-century modern house facade, symmetrical window grid, flat roofline, single centered front door, small concrete step, plain neutral background, soft even lighting, no cast shadows, clipped flat vegetation shapes on either side
```

## isometric.png

```
Style: A polished isometric 3D rendering with warm indie game charm, presented as a self-contained circular or rounded-square diorama floating in empty space, soft stylized low-poly to mid-poly geometry with clean rounded edges, gentle ambient occlusion and soft shadows rather than harsh realism, a warm inviting color palette with painterly texture work, miniature handcrafted game-level framing where the entire scene sits compactly within the diorama's base like a tiny world in a snow globe, soft volumetric lighting and glowing particle effects, charming exaggerated proportions on characters giving them a friendly storybook quality despite spooky subject matter, tilt-shift depth of field enhancing the toy-like miniature feel, the diorama's edges clearly defined with a visible base or platform rather than bleeding into open background.

Scenery: A vampire count's grand castle hall, a curved stone staircase with a worn crimson carpet runner leading up to a landing where he stands with his cloak spread wide like bat wings, his face pale with glowing amber-red eyes and a wide toothy grin. At the base of the stairs, a vampire hunter faces him in a defensive stance, a wooden stake gripped in one hand and a crucifix raised in the other, wearing a weathered long coat and wide-brimmed hat, his expression tense and determined. Small flickering candle sconces line the walls casting warm golden light pools across the stone floor, a large arched window on the back wall reveals a glowing full moon and a few small bats mid-flight against a deep indigo night sky, soft cobweb tufts tucked into the corners of wooden ceiling beams, clutter like a toppled suit of armor, a cracked stone urn, and scattered autumn leaves near the base of the stairs, a checkered stone floor in muted warm grays fading into soft shadow at the diorama's edges.
```

## watercolor.png

```
Style: A detailed and balanced vintage natural history illustration rendered in meticulous watercolor and fine ink on textured, cream-colored aged parchment paper, presented in a portrait orientation. 

Composition: A vibrant kingfisher bird bursting upwards from the surface of deep blue water, its wings fully extended in a powerful display of iridescent turquoise and teal feathers with distinct white tips. The bird holds a small, anatomically accurate European minnow firmly crosswise in its long beak, the fish rendered with natural proportions, a slender streamlined body, fine overlapping silver scales with a subtle pearlescent sheen, a clearly defined dorsal fin, pectoral and pelvic fins, a forked tail, a small round eye, and a closed mouth. The fish hangs naturally with a gentle curve and is realistically sized in relation to the kingfisher, appearing freshly caught. Water droplets and spray freeze in mid-air around the kingfisher, catching the bright sunlight like scattered diamonds. The chest features a splash of warm orange against the cool blue plumage. The water below is dark and rippled with concentric circles radiating outward from the point of impact. The atmosphere is dynamic and energetic, capturing the precise moment of a successful hunt with vivid, saturated colors while maintaining the scientific precision, lifelike anatomy, and observational accuracy characteristic of a classic 19th-century natural history illustration.
```

## gouache.png

```
Style: a playful gouache illustration with bold flat color shapes, visible brushwork, and rounded whimsical forms, in the manner of mid-century children's book art.
A cheerful player leans low over a rectangular billiard table, right arm extended and wrist cocked, aiming a slender wooden cue at a small sun-colored cue ball that glows pale yellow-white with thin radiating light lines. Racked in a triangle at the center of the table's deep navy playing surface, scattered with small white five-pointed stars, sits a cluster of eight balls painted as the solar system's planets: a tiny grey Mercury, a pale orange Venus, a blue-green Earth swirled with white clouds, a rust-red Mars, a large tan Jupiter banded in brown stripes, a golden Saturn ringed by a thin flat ellipse, a pale cyan Uranus, and a deep blue Neptune, arranged smallest to largest from the tip of the triangle toward its base. The table's dark wood rails frame six round pockets, one at each corner and one at the midpoint of each long side. Overhead, a round pendant lamp with a cream shade casts a warm circle of light across the starry surface, fading into soft shadow toward the table's edges. Behind, a plain ochre-colored wall fills the space, empty but for the lamp's cord descending from above.
```
