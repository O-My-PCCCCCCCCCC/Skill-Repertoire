package meteordevelopment.meteorclient.renderer.text;

import meteordevelopment.meteorclient.renderer.MeshBuilder;
import meteordevelopment.meteorclient.renderer.MeshRenderer;
import meteordevelopment.meteorclient.renderer.MeteorRenderPipelines;
import meteordevelopment.meteorclient.utils.render.color.Color;
import net.minecraft.client.Minecraft;

import java.nio.ByteBuffer;

/**
 * Replacement for the stock CustomTextRenderer. Renders every character (including CJK)
 * through FontFix's on-demand glyph loader, so Chinese text displays with any font.
 */
public class CustomTextRenderer implements TextRenderer {
    public static final Color SHADOW_COLOR = new Color(0, 0, 0, 200);

    private final MeshBuilder mesh;
    public final FontFace fontFace;
    private FontFix[] fonts;
    private FontFix font;

    private boolean building;
    private boolean scaleOnly;
    private double fontScale = 1;
    private double scale = 1;
    @SuppressWarnings("unused")
    private double alpha = 1;

    public CustomTextRenderer(FontFace fontFace) {
        this.fontFace = fontFace;
        this.mesh = new MeshBuilder(MeteorRenderPipelines.UI_TEXT);

        ByteBuffer buffer;
        try {
            buffer = fontFace.readToDirectByteBuffer();
        } catch (java.io.IOException e) {
            throw new RuntimeException(e);
        }
        fonts = new FontFix[5];
        for (int i = 0; i < fonts.length; i++) {
            fonts[i] = new FontFix(buffer, (int) Math.round(27 * ((i * 0.5) + 1)));
        }
    }

    @Override
    public void setAlpha(double alpha) {
        this.alpha = alpha;
    }

    @Override
    public void begin(double scale, boolean scaleOnly, boolean big) {
        if (building) throw new RuntimeException("CustomTextRenderer.begin() called twice");

        if (!scaleOnly) mesh.begin();

        if (big) {
            font = fonts[fonts.length - 1];
        }
        else {
            double scaleA = Math.floor(scale * 10) / 10;

            int scaleI;
            if (scaleA >= 3) scaleI = 5;
            else if (scaleA >= 2.5) scaleI = 4;
            else if (scaleA >= 2) scaleI = 3;
            else if (scaleA >= 1.5) scaleI = 2;
            else scaleI = 1;

            font = fonts[scaleI - 1];
        }

        this.building = true;
        this.scaleOnly = scaleOnly;

        this.fontScale = font.getHeight() / 27.0;
        this.scale = 1 + (scale - fontScale) / fontScale;
    }

    public void begin(double scale, boolean scaleOnly) {
        begin(scale, scaleOnly, false);
    }

    @Override
    public void begin(double scale) {
        begin(scale, false, false);
    }

    @Override
    public void begin() {
        begin(1, false, false);
    }

    @Override
    public void beginBig() {
        begin(1, false, true);
    }

    @Override
    public double getWidth(String text, int length, boolean shadow) {
        if (text.isEmpty()) return 0;

        FontFix font = building ? this.font : fonts[0];
        return (font.getWidth(text, length) + (shadow ? 1 : 0)) * scale;
    }

    @Override
    public double getWidth(String text, boolean shadow) {
        return getWidth(text, text.length(), shadow);
    }

    @Override
    public double getWidth(String text) {
        return getWidth(text, text.length(), false);
    }

    @Override
    public double getHeight(boolean shadow) {
        FontFix font = building ? this.font : fonts[0];
        return (font.getHeight() + 1 + (shadow ? 1 : 0)) * scale;
    }

    @Override
    public double getHeight() {
        return getHeight(false);
    }

    @Override
    public double render(String text, double x, double y, Color color, boolean shadow) {
        boolean wasBuilding = building;
        if (!wasBuilding) begin();

        double width;
        if (shadow) {
            int preShadowA = SHADOW_COLOR.a;
            SHADOW_COLOR.a = (int) (color.a / 255.0 * preShadowA);

            width = font.render(mesh, text, x + fontScale * scale, y + fontScale * scale, SHADOW_COLOR, scale);
            font.render(mesh, text, x, y, color, scale);

            SHADOW_COLOR.a = preShadowA;
        }
        else {
            width = font.render(mesh, text, x, y, color, scale);
        }

        if (!wasBuilding) end();
        return width;
    }

    @Override
    public double render(String text, double x, double y, Color color) {
        return render(text, x, y, color, false);
    }

    @Override
    public boolean isBuilding() {
        return building;
    }

    @Override
    public void end() {
        if (!building) throw new RuntimeException("CustomTextRenderer.end() called without calling begin()");

        if (!scaleOnly) {
            mesh.end();

            MeshRenderer.begin()
                .attachments(Minecraft.getInstance().getMainRenderTarget())
                .pipeline(MeteorRenderPipelines.UI_TEXT)
                .mesh(mesh)
                .sampler("u_Texture", font.texture.getTextureView(), font.texture.getSampler())
                .end();
        }

        building = false;
        scale = 1;
    }

    public void destroy() {}
}
