class Utils {
  static String joinURL(String url, String suf) {
    if (url.endsWith("/")) url = url.substring(0, url.length - 1);
    if (suf.startsWith("/")) suf = url.substring(1, suf.length);
    return "$url/$suf";
  }
}
